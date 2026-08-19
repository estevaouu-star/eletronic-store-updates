import { readFile, writeFile } from "node:fs/promises";

const manifestPath = process.env.ANDROID_MANIFEST_PATH || new URL("../android/app/src/main/AndroidManifest.xml", import.meta.url);
let manifest = await readFile(manifestPath, "utf8");

const additions = [
  '    <uses-permission android:name="android.permission.CAMERA" />',
  '    <uses-feature android:name="android.hardware.camera.any" android:required="false" />',
];

for (const addition of additions) {
  if (!manifest.includes(addition.trim())) manifest = manifest.replace("</manifest>", `${addition}\n</manifest>`);
}

await writeFile(manifestPath, manifest, "utf8");
console.log("Permissão nativa da câmera adicionada ao Eletromix Android.");
