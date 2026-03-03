module.exports = {
    version: "2.0",
    title: "College Management System",
    description: "A full-scale college management portal with an integrated AI assistant (AIRA) and automated WhatsApp parent notifications.",
    icon: "icon.png",
    menu: async (kernel, info) => {
        let installed = await kernel.exists(__dirname, "Main/Backend/.venv")
        let nodeInstalled = await kernel.exists(__dirname, "Main/whatsapp_service/node_modules")

        if (installed && nodeInstalled) {
            return [
                {
                    html: '<i class="fa-solid fa-power-off"></i> Start',
                    href: "start.json"
                },
                {
                    html: '<i class="fa-solid fa-plug"></i> Re-Install',
                    href: "install.json"
                }
            ]
        } else {
            return [
                {
                    html: '<i class="fa-solid fa-plug"></i> Install',
                    href: "install.json"
                }
            ]
        }
    }
}
