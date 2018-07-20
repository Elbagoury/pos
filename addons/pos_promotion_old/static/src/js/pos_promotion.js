odoo.define('pos_promotion', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var time = require('web.time');

    models.load_models([
        {
            model: 'pos.promotion',
            condition: function (self) {
                return self.config.promotion;
            },
            fields: [],
            domain: function (self) {
                return [
                    ['id', 'in', self.config.promotion_ids],
                    ['start_date', '<=', time.date_to_str(new Date()) + " " + time.time_to_str(new Date())],
                    ['end_date', '>=', time.date_to_str(new Date()) + " " + time.time_to_str(new Date())],
                ]
            },
            context: {'pos': true},
            loaded: function (self, promotions) {
                self.promotions = promotions;
                self.promotion_by_id = {};
                self.promotion_ids = []
                var i = 0;
                while (i < promotions.length) {
                    self.promotion_by_id[promotions[i].id] = promotions[i];
                    self.promotion_ids.push(promotions[i].id);
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.order',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts) {
                self.promotion_discount_order_by_id = {};
                self.promotion_discount_order_by_promotion_id = {};
                var i = 0;
                while (i < discounts.length) {
                    self.promotion_discount_order_by_id[discounts[i].id] = discounts[i];
                    if (!self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]]) {
                        self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]] = [discounts[i]]
                    } else {
                        self.promotion_discount_order_by_promotion_id[discounts[i].promotion_id[0]].push(discounts[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.category',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_category) {
                self.promotion_by_category_id = {};
                var i = 0;
                while (i < discounts_category.length) {
                    self.promotion_by_category_id[discounts_category[i].category_id[0]] = discounts_category[i];
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.quantity',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_quantity) {
                self.promotion_quantity_by_product_id = {};
                var i = 0;
                while (i < discounts_quantity.length) {
                    if (!self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]]) {
                        self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]] = [discounts_quantity[i]]
                    } else {
                        self.promotion_quantity_by_product_id[discounts_quantity[i].product_id[0]].push(discounts_quantity[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.condition',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, gift_conditions) {
                self.promotion_gift_condition_by_promotion_id = {};
                var i = 0;
                while (i < gift_conditions.length) {
                    if (!self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]]) {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]] = [gift_conditions[i]]
                    } else {
                        self.promotion_gift_condition_by_promotion_id[gift_conditions[i].promotion_id[0]].push(gift_conditions[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.gift.free',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, gifts_free) {
                self.promotion_gift_free_by_promotion_id = {};
                var i = 0;
                while (i < gifts_free.length) {
                    if (!self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]]) {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]] = [gifts_free[i]]
                    } else {
                        self.promotion_gift_free_by_promotion_id[gifts_free[i].promotion_id[0]].push(gifts_free[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.condition',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discount_conditions) {
                self.promotion_discount_condition_by_promotion_id = {};
                var i = 0;
                while (i < discount_conditions.length) {
                    if (!self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]]) {
                        self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]] = [discount_conditions[i]]
                    } else {
                        self.promotion_discount_condition_by_promotion_id[discount_conditions[i].promotion_id[0]].push(discount_conditions[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.discount.apply',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, discounts_apply) {
                self.promotion_discount_apply_by_promotion_id = {};
                var i = 0;
                while (i < discounts_apply.length) {
                    if (!self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]]) {
                        self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]] = [discounts_apply[i]]
                    } else {
                        self.promotion_discount_apply_by_promotion_id[discounts_apply[i].promotion_id[0]].push(discounts_apply[i])
                    }
                    i++;
                }
            }
        }, {
            model: 'pos.promotion.price',
            fields: [],
            condition: function (self) {
                return self.config.promotion;
            },
            domain: function (self) {
                return [['promotion_id', 'in', self.promotion_ids]]
            },
            context: {'pos': true},
            loaded: function (self, prices) {
                self.promotion_price_by_promotion_id = {};
                var i = 0;
                while (i < prices.length) {
                    if (!self.promotion_price_by_promotion_id[prices[i].promotion_id[0]]) {
                        self.promotion_price_by_promotion_id[prices[i].promotion_id[0]] = [prices[i]]
                    } else {
                        self.promotion_price_by_promotion_id[prices[i].promotion_id[0]].push(prices[i])
                    }
                    i++;
                }
            }
        }
    ]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
//         initialize: function (attributes, options) {
//             var self = this;
//             var res = _super_order.initialize.apply(this, arguments);
//             setInterval(function () {
//                 self.auto_build_promotion();
//                 console.log('auto build promotion')
//             }, 1000);
//             return res;
//         },
//         auto_build_promotion: function () {
//             if (!this.pos.building_promotion || this.pos.building_promotion == false) {
//                 var order = this.pos.get('selectedOrder');
//                 if (order && order.orderlines && order.orderlines.length && this.pos.config.promotion == true && this.pos.config.promotion_ids.length) {
//                     this.pos.building_promotion = true;
//                     order.compute_promotion()
//                     this.pos.building_promotion = false;
//                 }
//             }
//         },
        get_total_without_promotion_and_tax: function () {
            var rounding = this.pos.currency.rounding;
            var orderlines = this.orderlines.models
            var sum = 0
            var i = 0
            while (i < orderlines.length) {
                var line = orderlines[i];
                if (line.promotion && line.promotion == true) {
                    i++;
                    continue
                }
                sum += round_pr(line.get_unit_price() * line.get_quantity() * (1 - line.get_discount() / 100), rounding)
                i++
            }
            return sum;
        },
        compute_promotion: function () {
            var promotions = this.pos.promotions
            if (promotions) {
                for (var i = 0; i < promotions.length; i++) {
                    var type = promotions[i].type
                    var order = this;
                    if (order.orderlines.length) {
                        // discount filter by total of current order
                        if (type == '1_discount_total_order') {
                            order.compute_discount_total_order(promotions[i]);
                        }
                        // discount by category
                        if (type == '2_discount_category') {
                            order.compute_discount_category(promotions[i]);
                        }
                        // discount by quantity of product
                        if (type == '3_discount_by_quantity_of_product') {
                            order.compute_discount_by_quantity_of_products(promotions[i]);
                        }
                        // discount by pack
                        if (type == '4_pack_discount') {
                            order.compute_pack_discount(promotions[i]);
                        }
                        // free items filter by pack
                        if (type == '5_pack_free_gift') {
                            order.compute_pack_free_gift(promotions[i]);
                        }
                        // re-build price filter by quantity of product
                        if (type == '6_price_filter_quantity') {
                            order.compute_price_filter_quantity(promotions[i]);
                        }
                    }
                }
            }
        },
        export_for_printing: function () {
            var res = _super_order.export_for_printing.apply(this, arguments);
            if (this.promotion_amount) {
                res.promotion_amount = this.promotion_amount;
            }
            return res
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.promotion_amount) {
                json.promotion_amount = this.promotion_amount;
            }
            return json
        },
        product_quantity_by_product_id: function () {
            var lines_list = {};
            var lines = this.orderlines.models;
            var i = 0;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion) {
                    i++;
                    continue
                }
                if (!lines_list[line.product.id]) {
                    lines_list[line.product.id] = line.quantity;
                } else {
                    lines_list[line.product.id] += line.quantity;
                }
                i++;
            }
            return lines_list
        },
        // 1
        // check current order can apply discount by total order
        checking_apply_total_order: function (promotion) {
            var discount_lines = this.pos.promotion_discount_order_by_promotion_id[promotion.id];
            var total_order = this.get_total_without_promotion_and_tax();
            var discount_line_tmp = null;
            var discount_tmp = 0;
            if (discount_lines) {
                var i = 0;
                while (i < discount_lines.length) {
                    var discount_line = discount_lines[i];
                    if (total_order >= discount_line.minimum_amount && total_order >= discount_tmp) {
                        discount_line_tmp = discount_line;
                        discount_tmp = discount_line.minimum_amount
                    }
                    i++;
                }
            }
            return discount_line_tmp;
        },
        // 2
        // check current order can apply discount by categories
        checking_can_discount_by_categories: function (promotion) {
            var can_apply = false
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            if (!product || !this.pos.promotion_by_category_id) {
                return false;
            }
            for (i in this.pos.promotion_by_category_id) {
                var promotion_line = this.pos.promotion_by_category_id[i];
                var amount_total_by_category = 0;
                var z = 0;
                var lines = this.orderlines.models;
                while (z < lines.length) {
                    if (!lines[z].product.pos_categ_id) {
                        z++;
                        continue;
                    }
                    if (lines[z].product.pos_categ_id[0] == promotion_line.category_id[0]) {
                        amount_total_by_category += lines[z].get_price_without_tax();
                    }
                    z++;
                }
                if (amount_total_by_category > 0) {
                    can_apply = true
                }
            }
            return can_apply
        },
        // 3
        // check condition for apply discount by quantity product
        checking_apply_discount_filter_by_quantity_of_product: function (promotion) {
            var can_apply = false;
            var rules = this.pos.promotion_quantity_by_product_id;
            var product_quantity_by_product_id = this.product_quantity_by_product_id();
            for (product_id in product_quantity_by_product_id) {
                var rules_by_product_id = rules[product_id];
                if (rules_by_product_id) {
                    for (var i = 0; i < rules_by_product_id.length; i++) {
                        var rule = rules_by_product_id[i];
                        if (rule && product_quantity_by_product_id[product_id] >= rule.quantity) {
                            can_apply = true;
                        }
                    }
                }
            }
            return can_apply;
        },
        // 4 & 5
        // check pack free gift and pack discount product
        checking_pack_discount_and_pack_free_gift: function (rules) {
            var can_apply = true;
            var product_quantity_by_product_id = this.product_quantity_by_product_id();
            for (i = 0; i < rules.length; i++) {
                var rule = rules[i];
                var product_id = parseInt(rule.product_id[0]);
                var minimum_quantity = rule.minimum_quantity;
                if (!product_quantity_by_product_id[product_id] || product_quantity_by_product_id[product_id] < minimum_quantity) {
                    can_apply = false;
                }
            }
            return can_apply
        },
        // 6
        // check condition for apply price filter by quantity of product
        checking_apply_price_filter_by_quantity_of_product: function (promotion) {
            var condition = false;
            var rules = this.pos.promotion_price_by_promotion_id[promotion.id];
            var product_quantity_by_product_id = this.product_quantity_by_product_id();
            for (var i = 0; i < rules.length; i++) {
                var rule = rules[i];
                if (rule && product_quantity_by_product_id[rule.product_id[0]] && product_quantity_by_product_id[rule.product_id[0]] >= rule.minimum_quantity) {
                    condition = true;
                }
            }
            return condition;
        },

        // 1. compute discount filter by total order
        compute_discount_total_order: function (promotion) {
            var discount_line_tmp = this.checking_apply_total_order(promotion)
            var lines = this.orderlines.models; // remove old lines applied promotion by total order
            if (lines.length) {
                for (var j = 0; j < lines.length; j++) {
                    if (lines[j].promotion_discount_total_order) {
                        this.remove_orderline(lines[j]);
                    }
                }
            }
            if (discount_line_tmp == null) {
                return;
            }
            var total_order = this.get_total_without_promotion_and_tax();
            if (discount_line_tmp && total_order > 0) {
                var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                var price = -total_order / 100 * discount_line_tmp.discount
                if (product && price != 0) {
                    var options = {};
                    options.promotion_discount_total_order = true;
                    options.promotion = true;
                    options.promotion_reason = 'discount ' + discount_line_tmp.discount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_amount;
                    this.add_promotion(product, price, 1, options)
                }
            }
        },
        // 2. compute discount filter by product categories
        compute_discount_category: function (promotion) {
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            if (!product || !this.pos.promotion_by_category_id) {
                return;
            }
            var can_apply = this.checking_can_discount_by_categories(promotion);
            if (can_apply == false) {
                return;
            }
            var lines = this.orderlines.models;
            if (lines.length) { // remove all lines applied discount filter by category before
                var x = 0;
                while (x < lines.length) {
                    if (lines[x].promotion_discount_category) {
                        this.remove_orderline(lines[x]);
                    }
                    x++;
                }
            }
            for (i in this.pos.promotion_by_category_id) {
                var promotion_line = this.pos.promotion_by_category_id[i];
                var amount_total_by_category = 0;
                var z = 0;
                while (z < lines.length) {
                    if (!lines[z].product.pos_categ_id) {
                        z++;
                        continue;
                    }
                    if (lines[z].product.pos_categ_id[0] == promotion_line.category_id[0]) {
                        amount_total_by_category += lines[z].get_price_without_tax();
                    }
                    z++;
                }
                if (amount_total_by_category > 0) {
                    var price = -amount_total_by_category / 100 * promotion_line.discount
                    var options = {};
                    options.promotion_discount_category = true;
                    options.promotion = true;
                    options.promotion_reason = ' discount ' + promotion_line.discount + ' % ' + promotion_line.category_id[1];
                    this.add_promotion(product, price, 1, options)
                }
            }
        },
        // 3. compute discount filter by quantity of product
        compute_discount_by_quantity_of_products: function (promotion) {
            var check = this.checking_apply_discount_filter_by_quantity_of_product(promotion)
            if (check == false) {
                return;
            }
            var quantity_by_product_id = {}
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            var i = 0;
            var lines = this.orderlines.models;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_discount_by_quantity && line.promotion_discount_by_quantity == true) {
                    line.set_quantity('remove');
                    line.order.trigger('change', line.order);
                    i++;
                    continue
                }
                if (line.promotion) {
                    i++;
                    continue
                }
                if (!quantity_by_product_id[line.product.id]) {
                    quantity_by_product_id[line.product.id] = line.quantity;
                } else {
                    quantity_by_product_id[line.product.id] += line.quantity;
                }
                i++;
            }
            for (i in quantity_by_product_id) {
                var product_id = i;
                var promotion_lines = this.pos.promotion_quantity_by_product_id[product_id];
                if (!promotion_lines) {
                    continue;
                }
                var quantity_tmp = 0;
                var promotion_line = null;
                var j = 0
                for (j in promotion_lines) {
                    if (quantity_tmp <= promotion_lines[j].quantity && quantity_by_product_id[i] >= promotion_lines[j].quantity) {
                        promotion_line = promotion_lines[j];
                        quantity_tmp = promotion_lines[j].quantity
                    }
                }
                var lines = this.orderlines.models;
                var amount_total_by_product = 0;
                if (lines.length) {
                    var x = 0;
                    while (x < lines.length) {
                        if (lines[x].promotion) {
                            x++;
                            continue
                        }
                        if (lines[x].promotion_discount_by_quantity) {
                            this.remove_orderline(lines[x]);
                        }
                        if (lines[x].product.id == product_id && lines[x].promotion != true) {
                            amount_total_by_product += lines[x].get_price_without_tax()
                        }
                        x++;
                    }
                }
                if (amount_total_by_product > 0 && promotion_line) {
                    var price = -amount_total_by_product / 100 * promotion_line.discount
                    var options = {};
                    options.promotion_discount_by_quantity = true;
                    options.promotion = true;
                    options.promotion_reason = ' discount ' + promotion_line.discount + ' % when ' + promotion_line.product_id[1] + ' have quantity greater or equal ' + promotion_line.quantity;
                    this.add_promotion(product, price, 1, options)
                }
            }
        },

        // 4. compute discount product filter by pack items
        compute_pack_discount: function (promotion) {
            var promotion_condition_items = this.pos.promotion_discount_condition_by_promotion_id[promotion.id];
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            var check = this.checking_pack_discount_and_pack_free_gift(promotion_condition_items);
            var lines = this.orderlines.models;
            var i = 0;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_discount && line.promotion_discount == true) {
                    line.set_quantity('remove');
                    line.order.trigger('change', line.order);
                }
                i++;
            }
            if (check == true) {
                var discount_items = this.pos.promotion_discount_apply_by_promotion_id[promotion.id]
                if (!discount_items) {
                    return;
                }
                var i = 0;
                while (i < discount_items.length) {
                    var discount_item = discount_items[i];
                    var discount = 0;
                    var lines = this.orderlines.models;
                    for (x = 0; x < lines.length; x++) {
                        if (lines[x].promotion) {
                            continue;
                        }
                        if (lines[x].product.id == discount_item.product_id[0]) {
                            discount += lines[x].get_price_without_tax()
                        }
                    }
                    if (product && discount > 0) {
                        var price = -discount / 100 * discount_item.discount
                        var options = {};
                        options.promotion_discount = true;
                        options.promotion = true;
                        options.promotion_reason = 'discount ' + discount_item.product_id[1] + ' ' + discount_item.discount + ' % of Pack name: ' + promotion.name;
                        this.add_promotion(product, price, 1, options)
                    }
                    i++;
                }
            }
        },
        // 5. compute gift products filter by pack items
        compute_pack_free_gift: function (promotion) {
            var promotion_condition_items = this.pos.promotion_gift_condition_by_promotion_id[promotion.id];
            var check = this.checking_pack_discount_and_pack_free_gift(promotion_condition_items);
            var lines = this.orderlines.models;
            var i = 0;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_gift && line.promotion_gift == true) {
                    line.set_quantity('remove');
                    line.order.trigger('change', line.order);
                }
                i++;
            }
            if (check == true) {
                var gifts = this.pos.promotion_gift_free_by_promotion_id[promotion.id]
                if (!gifts) {
                    return;
                }
                var gift_amount=0.00
                var i = 0;
                while (i < gifts.length) {
                    var product = this.pos.db.get_product_by_id(gifts[i].product_id[0]);
                    if (product) {
//                         gift_amount+=product.mrp
                        var quantity = gifts[i].quantity_free                        
                        var add_gift_price = gifts[i].add_gift_price
                        var price = product.mrp - add_gift_price;                        
                        var options = {};
                        options.promotion_gift = true;
                        options.promotion = true;
                        options.promotion_reason = ' gift from: ' + promotion.name;
                        this.add_promotion(product, price, quantity, options)
                    }
                    i++;
                }
                this.orderlines.models.forEach(function(line){
                    promotion_condition_items.forEach(function(res){
                        if((line.promotion_gift==undefined || line.promotion_gift==false) && line.product.id==res.product_id[0])
                        {
//                             var gift_price = res.add_gift_price
//                             if((line.product.mrp-res.add_gift_price)!=line.price)
//                             {
                                var new_price=line.price -res.add_gift_price ;
    //                             line.set_gift_price(gift_price)
    //                             console.log('new price===',new_price,"gift price===",gift_price)
                                line.set_unit_price(new_price)
//                             }
                        }
                    })
                });
            }
        },
        // 6. compute and reset price of line filter by rule: price filter by quantity of product
        compute_price_filter_quantity: function (promotion) {
            var promotion_prices = this.pos.promotion_price_by_promotion_id[promotion.id]
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            var i = 0;
            var lines = this.orderlines.models;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_price_by_quantity && line.promotion_price_by_quantity == true) {
                    line.set_quantity('remove');
                    line.order.trigger('change', line.order);
                }
                i++;
            }
            if (promotion_prices) {
                var prices_item_by_product_id = {};
                for (var i = 0; i < promotion_prices.length; i++) {
                    var item = promotion_prices[i];
                    if (!prices_item_by_product_id[item.product_id[0]]) {
                        prices_item_by_product_id[item.product_id[0]] = [item]
                    } else {
                        prices_item_by_product_id[item.product_id[0]].push(item)
                    }
                }
                var quantity_by_product_id = this.product_quantity_by_product_id()
                var discount = 0;
                for (i in quantity_by_product_id) {
                    if (prices_item_by_product_id[i]) {
                        var quantity_tmp = 0
                        var price_item_tmp = null
                        // root: quantity line, we'll compare this with 2 variable quantity line greater minimum quantity of item and greater quantity temp
                        for (var j = 0; j < prices_item_by_product_id[i].length; j++) {
                            var price_item = prices_item_by_product_id[i][j];
                            if (quantity_by_product_id[i] >= price_item.minimum_quantity && quantity_by_product_id[i] >= quantity_tmp) {
                                quantity_tmp = price_item.minimum_quantity;
                                price_item_tmp = price_item;
                            }
                        }
                        if (price_item_tmp) {
                            var discount = 0;
                            var z = 0;
                            while (z < lines.length) {
                                var line = lines[z];
                                if (line.product.id == price_item_tmp.product_id[0]) {
                                    discount += line.get_price_without_tax() - (line.quantity * price_item_tmp.list_price)
                                }
                                z++;
                            }
                            if (discount > 0) {
                                var price = -discount;
                                var options = {};
                                options.promotion_price_by_quantity = true;
                                options.promotion = true;
                                options.promotion_reason = ' By greater or equal ' + price_item_tmp.minimum_quantity + ' ' + price_item_tmp.product_id[1] + ' applied price ' + price_item_tmp.list_price
                                this.add_promotion(product, price, 1, options)
                            }
                        }
                    }
                }
            }
        },
        // add promotion to current order
        add_promotion: function (product, price, quantity, options) {
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
            if (options.promotion) {
                line.promotion = options.promotion;
            }
            if (options.promotion_reason) {
                line.promotion_reason = options.promotion_reason;
            }
            if (options.promotion_discount_total_order) {
                line.promotion_discount_total_order = options.promotion_discount_total_order;
            }
            if (options.promotion_discount_category) {
                line.promotion_discount_category = options.promotion_discount_category;
            }
            if (options.promotion_discount_by_quantity) {
                line.promotion_discount_by_quantity = options.promotion_discount_by_quantity;
            }
            if (options.promotion_discount) {
                line.promotion_discount = options.promotion_discount;
            }
            if (options.promotion_gift) {
                line.promotion_gift = options.promotion_gift;
            }
            if (options.promotion_price_by_quantity) {
                line.promotion_price_by_quantity = options.promotion_price_by_quantity;
            }
            line.set_quantity(quantity);
            line.set_unit_price(price);
            this.orderlines.add(line);
            this.trigger('change', this);
        },
        current_order_can_apply_promotion: function () {
            var can_apply = null;
            for (var i = 0; i < this.pos.promotions.length; i++) {
                var promotion = this.pos.promotions[i];
                if (promotion['type'] == '1_discount_total_order' && this.checking_apply_total_order(promotion)) {
                    can_apply = true;
                }
                else if (promotion['type'] == '2_discount_category' && this.checking_can_discount_by_categories(promotion)) {
                    can_apply = true;
                }
                else if (promotion['type'] == '3_discount_by_quantity_of_product' && this.checking_apply_discount_filter_by_quantity_of_product(promotion)) {
                    can_apply = true;
                }
                else if ((promotion['type'] == '4_pack_discount' || promotion['type'] == '5_pack_free_gift') && (this.pos.promotion_discount_condition_by_promotion_id[promotion.id] || [])) {
                    var promotion_condition_items = true;
                }
                else if (promotion['type'] == '6_price_filter_quantity' && this.checking_apply_price_filter_by_quantity_of_product(promotion)) {
                    can_apply = true;
                }
            }
            return can_apply;
        }
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        init_from_JSON: function (json) {
            if (json.promotion) {
                this.promotion = json.promotion;
            }
            if (json.promotion_reason) {
                this.promotion_reason = json.promotion_reason;
            }
            if (json.promotion_discount_total_order) {
                this.promotion_discount_total_order = json.promotion_discount_total_order;
            }
            if (json.promotion_discount_category) {
                this.promotion_discount_category = json.promotion_discount_category;
            }
            if (json.promotion_discount_by_quantity) {
                this.promotion_discount_by_quantity = json.promotion_discount_by_quantity;
            }
            if (json.promotion_gift) {
                this.promotion_gift = json.promotion_gift;
            }
            if (json.promotion_discount) {
                this.promotion_discount = json.promotion_discount;
            }
            if (json.promotion_price_by_quantity) {
                this.promotion_price_by_quantity = json.promotion_price_by_quantity;
            }
            if(json.sales_person)
            {
                this.sales_person=json.sales_person
            }
            return _super_orderline.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function () {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            if (this.promotion) {
                json.promotion = this.promotion;
            }
            if (this.promotion_reason) {
                json.promotion_reason = this.promotion_reason;
            }
            if (this.promotion_discount_total_order) {
                json.promotion_discount_total_order = this.promotion_discount_total_order;
            }
            if (this.promotion_discount_category) {
                json.promotion_discount_category = this.promotion_discount_category;
            }
            if (this.promotion_discount_by_quantity) {
                json.promotion_discount_by_quantity = this.promotion_discount_by_quantity;
            }
            if (this.promotion_gift) {
                json.promotion_gift = this.promotion_gift;
//                 var product = this.pos.db.get_product_by_id(json.product_id);
//                 json.price_unit=product.mrp
            }
            if (this.promotion_discount) {
                json.promotion_discount = this.promotion_discount;
            }
            if (this.promotion_price_by_quantity) {
                json.promotion_price_by_quantity = this.promotion_price_by_quantity;
            }
            if(this.sales_person)
            {
                json.sales_person=this.sales_person
            }
            return json;
        },
        export_for_printing: function () {
            var res = _super_orderline.export_for_printing.apply(this, arguments);
            if (this.promotion) {
                res.promotion = this.promotion;
                res.promotion_reason = this.promotion_reason;
            }
            return res
        },
        can_be_merged_with: function (orderline) {
            var res=_super_orderline.can_be_merged_with.apply(this, arguments);
            if (this.promotion) {
                return false;
            }
            return res
        }
    });
    screens.OrderWidget.include({
        update_summary: function () {
            this._super();
            var order = this.pos.get('selectedOrder');
            if (order && order.orderlines && order.orderlines.length && this.pos.config.promotion == true && this.pos.config.promotion_ids.length) {
                var lines = order.orderlines.models;
                var promotion_amount = 0;
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i]
                    if (line.promotion) {
                        promotion_amount += line.get_price_without_tax()
                    }
                }
                if (order && this.el.querySelector('.promotion_amount')) {
                    this.el.querySelector('.promotion_amount').textContent = round_pr(promotion_amount, this.pos.currency.rounding);
                    order.promotion_amount = round_pr(promotion_amount, this.pos.currency.rounding);
                }
                var can_apply = order.current_order_can_apply_promotion();
                var buttons = this.getParent().action_buttons;
                if (buttons && buttons.button_promotion) {
                    buttons.button_promotion.highlight(can_apply);
                }
            }
        }
    });
    var button_promotion = screens.ActionButtonWidget.extend({
        template: 'button_promotion',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order) {
                order.compute_promotion()
            }
        }
    });
    screens.define_action_button({
        'name': 'button_promotion',
        'widget': button_promotion,
        'condition': function () {
            return this.pos.config.promotion == true && this.pos.promotion_ids.length && this.pos.promotion_ids.length >= 1;
        },
    });
    
    
    


});
