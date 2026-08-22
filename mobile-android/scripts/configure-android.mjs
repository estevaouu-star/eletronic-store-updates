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
  '    <uses-feature android:name="android.hardware.camera.any" android:required="false" />',
];

for (const addition of additions) {
  if (!manifest.includes(addition.trim())) manifest = manifest.replace("</manifest>", `${addition}\n</manifest>`);
}

await writeFile(manifestPath, manifest, "utf8");

const javaDirectory = join(androidRoot, "app/src/main/java/br/com/eletromix/mobile");
const mainActivityPath = join(javaDirectory, "MainActivity.java");
const permissionsPluginPath = join(javaDirectory, "EletromixPermissionsPlugin.java");

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
  mainActivityPath,
  `package br.com.eletromix.mobile;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        registerPlugin(EletromixPermissionsPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
`,
  "utf8",
);

console.log("Permissão e solicitação nativa da câmera configuradas no Eletromix Android.");
