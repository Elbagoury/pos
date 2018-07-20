odoo.define('pos_screen.pumps', function (require) {
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


    // START LOAD BACKEND OBJECT
    models.load_models({
        model: 'dom.pump',
        fields: [],
        domain: [['is_active','=',true]],
        loaded: function(self,pump){
            self.pump = pump
        },
    });

    models.load_models({
        model: 'dom.nozle',
        fields: [],
        domain: [['is_active','=',true]],
        loaded: function(self,nozle){
            self.nozle = nozle
        },
    });
    // END LOAD BACKEND OBJECT

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({

        get_nozle_by_id: function(nozle_id){
            console.log('in pumps');
            
            var total_nozles = this.nozle;

            for(var i=0; i<total_nozles.length; i++){

                if (total_nozles[i].id == nozle_id){
                    return total_nozles[i];
                }
            }

            return false;
        },

        nozle_confirmation_with_db: function(nozle_id, status){

            if (nozle_id){
                new Model('dom.nozle').call('get_nozle_request_from_pos', [parseInt(nozle_id), status]).then(function(callback) {
                    console.log(callback);
                });
            } 

        },

        change_nozle_state: function(nozle_id, state){
            var nozle = this.get_nozle_by_id(nozle_id)
            if (state == 'approve'){
                nozle.state = 'reserved'
            } else {
                nozle.state = state
            }
            this.change_nozle_image_according_to_state(nozle);
        },

        change_nozle_image_according_to_state: function(nozle){
            var nozle_div = $("[data-nozle-id='"+nozle.id+"']")
            if (nozle.state == 'idle'){
                var nozle_img = nozle_div.find('img').attr('src', window.location.origin + '/web/image?model=dom.nozle&field=image1&id='+ nozle.id)
                return window.location.origin + '/web/image?model=dom.nozle&field=image1&id='+ nozle.id;
            }
            if (nozle.state == 'requested'){
                var nozle_img = nozle_div.find('img').attr('src', "/point_of_sale/static/src/img/requested.gif")
                return "/point_of_sale/static/src/img/requested.gif"
            }
            if (nozle.state == 'reserved'){
                var nozle_img = nozle_div.find('img').attr('src', "/point_of_sale/static/src/img/reserved.png")
                return "/point_of_sale/static/src/img/reserved.png"
            }
            if (nozle.state == 'denied'){
                var nozle_img = nozle_div.find('img').attr('src', "/point_of_sale/static/src/img/idle.png")
                return "/point_of_sale/static/src/img/idle.png"
            }
            return "/point_of_sale/static/src/img/idle.png"
        },

        open_nozle_approval_pop_up: function(nozle_id){

            var self = this;
            var nozle = self.get_nozle_by_id(nozle_id);
            if (nozle.state == 'requested'){
                self.gui.show_popup('nozle-approval', {
                    'title': nozle.name, 
                    'id': nozle.id, 
                    'nozle': nozle.name,
                    'image_url': "data:image/png;base64,"+nozle.image
                });
            }
        },

        get_nozles_by_pump: function(pump){
            var nozle_list = []
            var total_nozles = this.nozle;
            for(var i = 0, len = total_nozles.length; i < len; i++){
                if ((total_nozles[i].dom_pump_id) && (total_nozles[i].dom_pump_id[0] == pump.id)){
                    nozle_list.push(total_nozles[i])
                }
            }
            return nozle_list
        },

        get_pump_by_nozle: function(nozle){

            for (var i=0; i<this.pump.length; i++){

                var pump_nozle_ids = this.pump[i].dom_nozle_ids;

                for (var j=0; j<pump_nozle_ids.length;j++){
                    if (nozle.id == pump_nozle_ids[j]){
                        return this.pump[i];
                    }
                }
            }
        },

        get_nozle_image_url: function(nozle){
            return window.location.origin + '/web/image?model=dom.nozle&field=image1&id='+ nozle.id;
        },

        change_nozle_info: function(nozle_id, vehicle_info){
            var nozle = this.get_nozle_by_id(nozle_id);
            nozle.vehicle_info = vehicle_info
            new Model('dom.nozle').call('nozle_vehicle_info_in_reserved_state', [parseInt(nozle_id), vehicle_info]).then(function(callback) {
                console.log(callback);
            });
        },

        change_nozle_capacity_info: function(notifications){
            if (!(notifications.hasOwnProperty("nozle_id") && notifications.hasOwnProperty("available_fuel"))){
                return false;
            } else {
                var nozle = this.get_nozle_by_id(notifications['nozle_id']);
                var pump = this.get_pump_by_nozle(nozle);
                var available_fuel = notifications['available_fuel'] || 0;
                var consumed_fuel = notifications['consumed_fuel'] || 0;
                var left_fuel = notifications['left_fuel'] || 0;

                var fuel_capacity_div = $('#pump-'+pump.id)
                fuel_capacity_div.find('.available_fuel').text(available_fuel);
                fuel_capacity_div.find('.consumed_fuel').text(consumed_fuel);
                fuel_capacity_div.find('.left_fuel').text(left_fuel);
            }
        }
    });

    // START RENDER NOZLES AND PUMPS
    var DomPumpWidget = PosBaseWidget.extend({
        template: 'DomPumpWidget',

        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            this.pump_list = options.pump_list || null;
            this.bus_nozle = bus.bus;
            var nozle_channel_name = "pos.nozle_polling";
            var new_channel = this.get_nozle_full_channel_name(nozle_channel_name);
            this.bus_nozle.add_channel(new_channel);
            this.pos.ready.then(function () {
                self.start_nozle_longpolling();
            });
            this.click_nozle_handler = function(){
                var nozle_id = $('.nozle', this).data('nozle-id');
                self.pos.open_nozle_approval_pop_up(nozle_id);
            };
        },

        start_nozle_longpolling: function(){
            var self = this;
            this.bus_nozle.on("notification", this, this.on_nozle_notification); 
        },

        on_nozle_notification: function (notifications) {
            if (notifications){
                if (notifications[0][1].nozle_polling == 'pos.nozle_polling'){
                    var self = this;
                    var result = notifications[0][1];
                    var nozle = this.pos.get_nozle_by_id(result["nozle_id"]);
                    nozle.state = 'requested'
                    nozle.image = notifications[0][1].image
                    self.pos.change_nozle_image_according_to_state(nozle);
                    self.pos.change_nozle_capacity_info(notifications[0][1]);
$( "#fuel-tab" ).trigger( "click" );
                }
            }
        },

        get_nozle_full_channel_name: function(channel_name){
            return JSON.stringify([session.db, channel_name,String(this.pos.config.id)]);
        },

        replace: function($target){
            this.renderElement();
            var target = $target[0];
            target.parentNode.replaceChild(this.el,target);
        },

        renderElement: function(){
            var el_str  = QWeb.render(this.template, {widget: this});
            
            var el_node = document.createElement('div');
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];

            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;

            var pump_list_container = el_node.querySelector('.pump-list');

            for(var i = 0, len = this.pump_list.length; i < len; i++){
                var pump_nozle_container = document.createElement('div');
                    pump_nozle_container.className = "pump-nozle-block";

                    var pump_node = this.render_pump(this.pump_list[i]);
                    pump_nozle_container.appendChild(pump_node);

                    var nozles = this.pos.get_nozles_by_pump(this.pump_list[i]);
                    var nozles_node =this.render_nozle(nozles);

                    pump_nozle_container.appendChild(nozles_node);
                pump_list_container.appendChild(pump_nozle_container)
            }
        },

        render_nozle: function(nozles){
            var self = this;
            var nozles_node = document.createElement('div');
            nozles_node.className = "nozles-block";
            for (var i=0; i<nozles.length; i++){
                var nozle_node = document.createElement('div');
                var nozle_html = QWeb.render('Nozle',{ 
                    widget:  this, 
                    nozle: nozles[i],
                    image_url: self.pos.change_nozle_image_according_to_state(nozles[i]),
                });
                nozle_node.innerHTML = nozle_html;
                nozle_node = nozle_node.childNodes[1];
                nozle_node.addEventListener('click', this.click_nozle_handler);
                nozles_node.appendChild(nozle_node);
            }
            return nozles_node;
        },

        get_pump_image_url:function(pump){
            return window.location.origin + '/web/image?model=dom.pump&field=image&id='+pump.id;
        },

        render_pump: function(pump){
            var pump_html = QWeb.render('Pump',{ 
                widget:  this, 
                pump: pump,
                image_url: this.get_pump_image_url(pump),
            });
            var pump_node = document.createElement('div');
            pump_node.innerHTML = pump_html;
            pump_node = pump_node.childNodes[1];
            return pump_node;
        },

    });
    // END RENDER NOZLES AND PUMPS

    // START MAKE DIVISION ON PRODUCT SCREEN
    screens.ProductScreenWidget.include({
        start: function(){ 
            var self = this;
            this._super()
            this.dompump_widget = new DomPumpWidget(this,{pump_list: this.pos.pump});
            this.dompump_widget.replace(this.$('.placeholder-DomPumpWidget'));
        },
    });
    // END MAKE DIVISION ON PRODUCT SCREEN

    //START NOZZLE APPROVAL POPUP
    var NozleApprovalPopupWidget = PopupWidget.extend({
        template: 'NozleApprovalPopupWidget',

        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
            this.popup_cache = new screens.DomCache();
        },

        events: _.extend({}, PopupWidget.prototype.events, {
            'click .button.approve': 'click_approve',
            'click .button.denied': 'click_denied'
        }),

        click_approve: function(){
            var nozle_id = this.$('.id').val();
            var vehicle_info = this.$('input[name="vehicle_info"]').val();
            this.pos.change_nozle_state(nozle_id, 'approve');
            this.pos.nozle_confirmation_with_db(nozle_id, 'approve');
            this.pos.change_nozle_info(nozle_id, vehicle_info)
            this.gui.close_popup();
        },

        click_denied: function(){
            var nozle_id = this.$('.id').val();
            this.pos.change_nozle_state(nozle_id, 'idle');
            this.pos.nozle_confirmation_with_db(nozle_id, 'denied');
            this.gui.close_popup();
        },
    });

    gui.define_popup({name:'nozle-approval', widget: NozleApprovalPopupWidget});
    //START NOZZLE APPROVAL POPUP

});


