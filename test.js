const usb = require('usb');

// Vendor ID dan Product ID
const VENDOR_ID = 0x29DA; // Vendor ID perangkat
const PRODUCT_ID = 0x0007; // Product ID perangkat

// Fungsi untuk menangani perangkat baru yang terdeteksi
function handleDevice(device) {
    if (device.deviceDescriptor.idVendor === VENDOR_ID && device.deviceDescriptor.idProduct === PRODUCT_ID) {
        console.log('Digiducer device connected!');
        try {
            device.open();
            const usbInterface = device.interfaces[0];
            if (usbInterface.isKernelDriverActive()) {
                usbInterface.detachKernelDriver();
            }
            usbInterface.claim();
            console.log('Device claimed successfully.');
        } catch (err) {
            console.error('Error claiming device:', err);
        }
    }
}

// Listener untuk mendeteksi perangkat USB yang terhubung
usb.on('attach', (device) => {
    console.log('Device attached:', device);
    handleDevice(device);
});

// Listener untuk mendeteksi perangkat USB yang dilepas
usb.on('detach', (device) => {
    if (device.deviceDescriptor.idVendor === VENDOR_ID && device.deviceDescriptor.idProduct === PRODUCT_ID) {
        console.log('Digiducer device disconnected.');
    }
});

console.log('Listening for USB device changes...');
