odoo.define('bi_pos_gift_receipt.GiftReceiptDetailPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState } = owl;
    const { _lt } = require('@web/core/l10n/translation');
    const Popup = require('point_of_sale.ConfirmPopup');
    var utils = require('web.utils');

    class GiftReceiptDetailPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
        }

        confirm(){
            var self = this;
            var checked_ids = []
            var input_text_data = []
            var final_data = []
            var not_alpha = []
            var final_data_send = []
            let checkbox = document.getElementsByName("checkbox");
            let input_text = document.getElementsByName("input-text");
            for (let i = 0; i < checkbox.length; i++) {
               if (checkbox[i].checked == true){
                    checked_ids.push(parseInt(checkbox[i].id))
               }
            }
            if(checked_ids.length <= 0){
                alert("please select the lines")
            } else{
                if(input_text.length > 0){
                    for (let i = 0; i < input_text.length; i++) {
                        if(input_text[i].value){
                            if(!input_text[i].value.match(/[A-Z|a-z|ü|é]/i)){
                                not_alpha.push(input_text[i])
                            }
                        }
                    }
                }
                if(not_alpha.length > 0){
                    alert("please add the alphabatic in input")
                } else{
                    if(input_text.length > 0){
                        for (let i = 0; i < input_text.length; i++) {
                            if(input_text[i].value){
                                input_text_data.push({'id': parseInt(input_text[i].id), 'value':input_text[i].value})
                            }
                        }
                    }
                    for(var data of checked_ids){
                        for(var input_data of input_text_data){
                            if(data == input_data['id']){
                                final_data.push(input_data);
                            }
                        }
                    }
                    if(final_data.length > 0){
                        const groupedData = {};
                        final_data.forEach(item => {
                            if (!groupedData[item.value]) {
                                for(var line1 of self.env.pos.get_order().get_orderlines()){
                                    if(line1.id == item.id){
                                        var name = line1.product.display_name
                                    }
                                }
                                groupedData[item.value] = [[item.id, name]];
                            } else {
                                for(var line1 of self.env.pos.get_order().get_orderlines()){
                                    if(line1.id == item.id){
                                        var name = line1.product.display_name
                                    }
                                }
                                groupedData[item.value].push([item.id, name]);
                            }
                        });
                        final_data_send.push(groupedData)
                        var dict1 = {'data_list' : final_data_send}
                        this.env.pos.get_order().set_split_data(dict1);
                        this.cancel();
                    } else{
                        alert("please add the input text.")
                    }
                }
            }
        }
        cancel(){
            this.env.posbus.trigger('close-popup', {
                popupId: this.props.id,
                response: { confirmed: false, payload: null },
            });
        }
    }
    GiftReceiptDetailPopup.template = 'GiftReceiptDetailPopup';
    GiftReceiptDetailPopup.defaultProps = {
        confirmText: _lt('Split'),
        cancelText: _lt('Cancel'),
        body: '',
    };
    Registries.Component.add(GiftReceiptDetailPopup);
    return GiftReceiptDetailPopup;
});
