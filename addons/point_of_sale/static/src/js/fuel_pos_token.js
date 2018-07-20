odoo.define('fuel_pos_token.fuel_pos_token', function (require) {
"use strict";

    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    // Generate Car wash token
    var generate_car_wash_token = screens.ActionButtonWidget.extend({
	    template: 'car_wash_generate_token',
	    button_click: function() {
            // temp random token generate
            var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            var token = '';
            for(var i = 0; i < 10; i++) {

                // random from 0 to length of whitelist
                var randomCharIndex = Math.floor(Math.random() * chars.length);

                // append a random character to the temp string
                token += chars[randomCharIndex];
            }
		    this.gui.show_popup('confirm', {
		        'title': _t('Generate Car wash '),
		        'body':  _t('Generate car wash Token : ')+token,

		    });
	    },
	});

	screens.define_action_button({
	    'name': 'generate_car_wash_token',
	    'widget': generate_car_wash_token
	});

    // Generate Coffee token
    var generate_coffee_token = screens.ActionButtonWidget.extend({
        template: 'generate_coffee_token',
        button_click: function() {
            // temp random token generate
            var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            var token = '';
            for(var i = 0; i < 10; i++) {
                // random from 0 to length of whitelist
                var randomCharIndex = Math.floor(Math.random() * chars.length);

                // append a random character to the temp string
                token += chars[randomCharIndex];
            }
            this.gui.show_popup('confirm', {
                'title': _t('Generate Coffee Token'),
                'body':  _t('Generate Coffee Token : ')+token,
            });
        },
    });

    screens.define_action_button({
        'name': 'generate_coffee_token',
        'widget': generate_coffee_token
    });	

   
});
