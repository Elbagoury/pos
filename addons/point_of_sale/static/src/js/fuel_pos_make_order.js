odoo.define('fuel_pos_make_order.fuel_pos_make_order', function (require) {
"use strict";

   var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups')
    var core = require('web.core');
    var Model = require('web.DataModel');

    var bus = require('bus.bus');
    var session = require('web.session');

    var QWeb = core.qweb;
    var _t = core._t;



    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function() {
            var self =this;
            _super_posmodel.initialize.apply(this, arguments);

            this.ready.then(function () {
                self.start_make_order_longpolling();
            });
        },

        start_make_order_longpolling: function(){
            var self = this;
            this.bus_make_order = bus.bus;
            var make_order_channel_name = "pos.make_order";
            var make_order_channel = this.get_make_order_full_channel_name(make_order_channel_name);
            this.bus_make_order.add_channel(make_order_channel);
            this.bus_make_order.on("notification", this, this.on_notification_make_order);
        },

        on_notification_make_order: function (notifications) {
            if (notifications){
                 if (notifications[0][1].nozle_polling == 'pos.make_order'){
                    var self = this;
                    var result = notifications[0][1];
                    this.set_order_respect_to_nozle(result);
                    this.change_nozle_capacity_info(notifications[0][1])
                }
            }
        },
        
        set_order_respect_to_nozle: function(result){
            var nozle = this.get_nozle_by_id(result["nozle_id"]);
            var order = this.add_new_order();
            this.make_nozle_in_idle_state(nozle.id)
            order.set_nozle_of_order(nozle);
            order.set_vehicle_info_of_order(nozle.vehicle_info);
            var pump = this.get_pump_by_nozle(nozle)

            if(nozle.product_id){
                var product = this.db.get_product_by_id(nozle.product_id[0]);
                order.add_product(product, {quantity: result['quantity']});
            } else {
                console.log("Nozle haven't any product.")
            }
        },

        get_make_order_full_channel_name: function(channel_name){
            return JSON.stringify([session.db, channel_name, String(this.config.id)]);
        },

        make_nozle_in_idle_state: function(nozle_id){
            if (!nozle_id){
                console.log("Not any selected Nozle!");
                return false;
            }
            this.change_nozle_state(nozle_id, 'idle');
            new Model('dom.nozle').call('make_nozle_in_idle_state', [parseInt(nozle_id)]).then(function(callback) {
                console.log(callback);
            });
        },
    });
    
    
    models.load_fields("pos.order", ['nozle_id', 'vehicle_info']);
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.nozle_id = this.nozle_id || false;
            this.vehicle_info = this.vehicle_info || false;
        },
    
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.nozle_id = json.nozle_id || false;
            this.vehicle_info = json.vehicle_info || false;
        },
    
        set_nozle_of_order: function(nozle){
            this.nozle_id = nozle.id;
            this.trigger('change', this); 
        },
    
        get_nozle_of_order: function(){
            return this.nozle_id;
        },

        set_vehicle_info_of_order: function(vehicle_info){
            this.vehicle_info = vehicle_info;
            this.trigger('change', this);
        },

        get_vehicle_info_of_order: function(){
            return this.vehicle_info;
        },

        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.nozle_id = this.nozle_id;
            json.vehicle_info = this.vehicle_info;
            return json;
        },
    });

    screens.PaymentScreenWidget.include({
        finalize_validation: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order()
            this.pos.make_nozle_in_idle_state(order.nozle_id)
        },
    });
});
