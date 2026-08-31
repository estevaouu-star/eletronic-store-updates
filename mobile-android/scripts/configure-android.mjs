import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const androidRoot = process.env.ANDROID_PROJECT_PATH
  ? process.env.ANDROID_PROJECT_PATH
  : fileURLToPath(new URL("../android", import.meta.url));
const manifestPath = process.env.ANDROID_MANIFEST_PATH || join(androidRoot, "app/src/main/AndroidManifest.xml");
let manifest = await readFile(manifestPath, "utf8");

const additions = [
  '    <uses-permission android:name="android.permission.CAMERA" />',
  '    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />',
  '    <uses-feature android:name="android.hardware.camera.any" android:required="false" />',
];

for (const addition of additions) {
  if (!manifest.includes(addition.trim())) manifest = manifest.replace("</manifest>", `${addition}\n</manifest>`);
}

await writeFile(manifestPath, manifest, "utf8");

const javaDirectory = join(androidRoot, "app/src/main/java/br/com/eletromix/mobile");
const mainActivityPath = join(javaDirectory, "MainActivity.java");
const permissionsPluginPath = join(javaDirectory, "EletromixPermissionsPlugin.java");
const filesPluginPath = join(javaDirectory, "EletromixFilesPlugin.java");

await mkdir(javaDirectory, { recursive: true });
await writeFile(
  permissionsPluginPath,
  `package br.com.eletromix.mobile;

import android.Manifest;
import com.getcapacitor.Plugin;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;

@CapacitorPlugin(
    name = "EletromixPermissions",
    permissions = {
        @Permission(alias = "camera", strings = { Manifest.permission.CAMERA })
    }
)
public class EletromixPermissionsPlugin extends Plugin {}
`,
  "utf8",
);

await writeFile(
  filesPluginPath,
  `package br.com.eletromix.mobile;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

@CapacitorPlugin(name = "EletromixFiles")
public class EletromixFilesPlugin extends Plugin {
    @PluginMethod
    public void savePdf(PluginCall call) {
        String base64 = call.getString("base64", "");
        String fileName = call.getString("fileName", "comprovante-eletromix.pdf");
        fileName = fileName.replaceAll("[^a-zA-Z0-9._-]", "-");
        if (!fileName.toLowerCase().endsWith(".pdf")) fileName += ".pdf";
        try {
            byte[] bytes = Base64.decode(base64, Base64.DEFAULT);
            if (bytes.length < 5 || bytes[0] != '%' || bytes[1] != 'P' || bytes[2] != 'D' || bytes[3] != 'F') {
                call.reject("O arquivo recebido não é um PDF válido.");
                return;
            }
            String savedPath;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentResolver resolver = getContext().getContentResolver();
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, fileName);
                values.put(MediaStore.Downloads.MIME_TYPE, "application/pdf");
                values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/Eletromix");
                values.put(MediaStore.Downloads.IS_PENDING, 1);
                Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new IllegalStateException("Não foi possível criar o arquivo em Downloads.");
                try (OutputStream output = resolver.openOutputStream(uri)) {
                    if (output == null) throw new IllegalStateException("Não foi possível abrir o arquivo para gravação.");
                    output.write(bytes);
                } catch (Exception error) {
                    resolver.delete(uri, null, null);
                    throw error;
                }
                values.clear();
                values.put(MediaStore.Downloads.IS_PENDING, 0);
                resolver.update(uri, values, null, null);
                savedPath = "Downloads/Eletromix/" + fileName;
            } else {
                File directory = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "Eletromix");
                if (!directory.exists() && !directory.mkdirs()) throw new IllegalStateException("Não foi possível criar Downloads/Eletromix.");
                File target = new File(directory, fileName);
                try (OutputStream output = new FileOutputStream(target)) { output.write(bytes); }
                savedPath = target.getAbsolutePath();
            }
            JSObject result = new JSObject();
            result.put("saved", true);
            result.put("path", savedPath);
            call.resolve(result);
        } catch (Exception error) {
            call.reject("Não foi possível salvar o PDF: " + error.getMessage(), error);
        }
    }
}
`,
  "utf8",
);

await writeFile(
  mainActivityPath,
  `package br.com.eletromix.mobile;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        registerPlugin(EletromixPermissionsPlugin.class);
        registerPlugin(EletromixFilesPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
`,
  "utf8",
);

console.log("Câmera e salvamento nativo de PDF configurados no Eletromix Android.");
