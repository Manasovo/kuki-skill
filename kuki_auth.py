""" A simple and thin Python library for the Kuki Web API """

import { HttpClient } from '@angular/common/http';

export class AuthExample {

    constructor(private httpClient: HttpClient) {
    }

    public auth() {
        const deviceType = 'webbrowser'; """ vyber ze 'smarttv', 'mobile', 'fix', 'webbrowser '"""
        const serial = this.generateSerial(); """ genertor serialu, viz nize """
        const deviceModel = 'DOPLNIT DEVICE MODEL'; """ pro web pouzivame: window.navigator.userAgent.substring(0, 250); """
        const product_name = 'DOPLNIT PRODUCT NAME'; """ // pro web pouzivame: WEBBROWSER """
        const mac = '00:00:00:00:00:00';
        const versionVw = '1.0';
        const versionPortal = '2.0.14';
        const bootMode = 'unknown';
        const apiUrl = 'https://as.kukacka.netbox.cz/api-v2/'; """ API URL, pro ostrou https://as.kuki.cz/api-v2/ """
        this.httpClient
            .post(apiUrl + 'register', {
                sn: serial,
                device_type: deviceType,
                device_model: deviceModel,
                product_name: product_name,
                mac: mac,
                version_fw: versionVw,
                version_portal: versionPortal,
                boot_mode: bootMode,
                claimed_device_id: serial
            }).subscribe((response: any) => {
            if (response.state === 'NOT_REGISTERED') {  """ nova registrace, nutno naparovat """
                console.log('Parovaci kod: ', response.reg_token);
                console.log('Registracni odkaz pro parovani: ', response.registration_url_web);
            } else { // jsem jiz zaregistrovany, mohu pouzivat session key
                if (response.state !== 'NOT_REGISTERED') {
                    console.log('session_key', response.session_key);
                }
            }
        });
    }

    private generateSerial(): string {
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let serial = 'kuki2.0_';
        for (let i = 0; i < 56; i++) {
            serial += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return serial;
    }
}
