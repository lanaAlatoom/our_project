/* @odoo-module */

import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { patch } from "@web/core/utils/patch";

const applyWhenMounted = async ({ el, container, callback }) => {
    const elClone = el.cloneNode(true);
    const sameClassElements = container.querySelectorAll(`.${[...el.classList].join(".")}`);

    sameClassElements.forEach(element => {
        element.remove();
    });
    container.appendChild(elClone);
    const res = await callback(elClone);
    return res;
};


const htmlToCanvas = async (el, options) => {
    el.classList.add(options.addClass || "");
    return await applyWhenMounted({
        el,
        container: document.querySelector(".render-container"),
        callback: async (el) =>
            await html2canvas(el, {
                height: Math.ceil(el.clientHeight),
                width: Math.ceil(el.clientWidth),
                scale: 3,
            }),
    });
};


patch(BasePrinter.prototype, {
    async printReceipt(receipt) {
        if (!receipt) return;

        this.receiptQueue.push(receipt);

        let printResult;
        while (this.receiptQueue.length > 0) {
            receipt = this.receiptQueue.shift();

            const contactElement = receipt.querySelector('.pos-receipt-contact');
            if (contactElement) {
                contactElement.style.fontSize = '24px';
            }

            const image = this.processCanvas(await htmlToCanvas(receipt, { addClass: "pos-receipt-print" }));

            const newReceipt = this.config ? { data: receipt.outerHTML, isBase64: false } : { data: image, isBase64: true };

            try {
                printResult = await this.sendPrintingJob(newReceipt);
            } catch (error) {
                console.error("Error sending printing job:", error);
                return this.getActionError();
            }

            if (!printResult || printResult.result === false) {
                console.error("Printing job failed:", printResult);
                return this.getResultsError(printResult);
            }
        }

        return { successful: true };
    }
});