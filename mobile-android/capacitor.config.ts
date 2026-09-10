import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "br.com.eletromix.mobile",
  appName: "Eletromix",
  webDir: "www",
  server: {
    url: "https://eletromix-mobile.estevaouu.chatgpt.site",
    cleartext: false,
    allowNavigation: ["eletromix-mobile.estevaouu.chatgpt.site"],
  },
  android: {
    allowMixedContent: false,
    backgroundColor: "#111318",
  },
};

export default config;
