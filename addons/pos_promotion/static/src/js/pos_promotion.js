odoo.define('pos_promotion', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var time = require('web.time');

    var groupBy = (xs, key) => {
        return xs.reduce((rv, x) => {
            (rv[x[key]] = rv[x[key]] || []).push(x);
            return rv;
        }, {});
    };
    Array.prototype.groupBy = function (key) {
        return this.reduce((rv, x) => {
            (rv[x[key]] = rv[x[key]] || []).push(x);
            return rv;
        }, {});
    };
    // Array.prototype.groupBy = function (key) {
    //     return this.reduce((rv, x) => {
    //         (rv[x[key]] = rv[x[key]] || []).push(x);
    //         return rv;
    //     }, {});
    // };
    Array.prototype.max = function () {
        return Math.max.apply(null, this);
    };

    Array.prototype.min = function () {
        return Math.min.apply(null, this);
    };

    models.load_models([{
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
        context: {
            'pos': true
        },
        loaded: function (self, promotions) {
            self.promotions = promotions;
            self.scrap = {};
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
            return [
                ['promotion_id', 'in', self.promotion_ids]
            ]
        },
        context: {
            'pos': true
        },
        loaded: function (self, discounts) {
            console.log("pos.promotion.discount.order ", self, discounts);
            self.promotion_discount_order_by_id = {};
            self.promotion_discount_order_by_promotion_id = {};
            discounts.map(discount => {
                self.promotion_discount_order_by_id[discount.id] = discount;
                if (!self.promotion_discount_order_by_promotion_id[discount.promotion_id[0]]) {
                    self.promotion_discount_order_by_promotion_id[discount.promotion_id[0]] = [discount]
                } else {
                    self.promotion_discount_order_by_promotion_id[discount.promotion_id[0]].push(discount)
                }
            })
        }
    }, {
        model: 'pos.promotion.value.reduction.order',
        fields: [],
        condition: function (self) {
            return self.config.promotion;
        },
        domain: function (self) {
            return [
                ['promotion_id', 'in', self.promotion_ids]
            ]
        },
        context: {
            'pos': true
        },
        loaded: function (self, reductions) {

            console.log("pos.promotion.value.reduction.order", self, reductions);
            self.promotion_reduction_order_by_id = {};
            self.promotion_reduction_order_by_promotion_id = {};
            reductions.map(reduction => {
                self.promotion_reduction_order_by_id[reduction.id] = reduction;
                if (!self.promotion_reduction_order_by_promotion_id[reduction.promotion_id[0]]) {
                    self.promotion_reduction_order_by_promotion_id[reduction.promotion_id[0]] = [reduction]
                } else {
                    self.promotion_reduction_order_by_promotion_id[reduction.promotion_id[0]].push(reduction)
                }
            })

            // self.promotion_by_category_id = {};
            // var i = 0;
            // while (i < discounts_category.length) {
            //     self.promotion_by_category_id[discounts_category[i].category_id[0]] = discounts_category[i];
            //     i++;
            // }
        }
    }, {
        model: 'pos.promotion.specified.goods.total',
        fields: [],
        condition: function (self) {
            return self.config.promotion;
        },
        domain: function (self) {
            return [
                ['promotion_id', 'in', self.promotion_ids]
            ]
        },
        context: {
            'pos': true
        },
        loaded: function (self, specified_goods) {
            console.log("pos.promotion.specified.goods.total", self, specified_goods);
            if (!self.promotion_combo_product) {
                self.promotion_combo_product = [];
            }
            if (!self.promotionIds) {
                self.promotionIds = {};
            }
            if (!self.allPromotions) {
                self.allPromotions = {};
            }
            if (!(self.promotionsToApply && self.promotionsToApply.length)) {
                self.promotionsToApply = [];
            }
            if (specified_goods && specified_goods.length) {
                self.promotionIds['specified_goods'] = specified_goods[0].promotion_id[0];
                self.promotionIds[specified_goods[0].promotion_id[0]] = 'specified_goods';
                self.allPromotions[self.promotionIds['specified_goods']] = {};
                specified_goods.map(specifiedGoods => {
                    // if (!self.allPromotions[specifiedGoods.promotion_id[0]]) {
                    let products = {};
                    specifiedGoods.product_ids.map(data => {
                        products[data] = {
                            id: data,
                            count: 0
                        }
                        self.promotion_combo_product.push({
                            promotion_id: self.promotionIds['specified_goods'],
                            combo_id: specifiedGoods.id,
                            product_id: data,
                            price: specifiedGoods.price,
                            count: 0
                        })
                    });
                    self.allPromotions[self.promotionIds['specified_goods']][specifiedGoods.id] = {
                        display_name: specifiedGoods.display_name,
                        id: specifiedGoods.id,
                        promotion_id: specifiedGoods.promotion_id[0],
                        promotion_name: specifiedGoods.promotion_id[1],
                        type: 'specified_goods',
                        price: specifiedGoods.price,
                        count: 0,
                        product_ids: products,
                        products: specifiedGoods.product_ids
                    }
                    // } else {
                    //     self.allPromotions[self.promotionIds['specified_goods']][specifiedGoods.id] = specifiedGoods
                    // }
                });
            }
        }
    }, {
        model: 'pos.promotion.number.items.price',
        fields: [],
        condition: function (self) {
            return self.config.promotion;
        },
        domain: function (self) {
            return [
                ['promotion_id', 'in', self.promotion_ids]
            ]
        },
        context: {
            'pos': true
        },
        loaded: function (self, number_items) {
            console.log("pos.promotion.number.items.price", self, number_items);
            if (!self.promotion_combo_product) {
                self.promotion_combo_product = [];
            }
            if (!self.promotionIds) {
                self.promotionIds = {};
            }
            if (!self.allPromotions) {
                self.allPromotions = {};
            }
            if (!(self.promotionsToApply && self.promotionsToApply.length)) {
                self.promotionsToApply = [];
            }
            if (number_items && number_items.length) {
                self.promotionIds['number_items'] = number_items[0].promotion_id[0];
                self.promotionIds[number_items[0].promotion_id[0]] = 'number_items';
                self.allPromotions[self.promotionIds['number_items']] = {};
                number_items.map(numberItems => {
                    // if (!self.allPromotions[numberItems.promotion_id[0]]) {
                    let products = {};
                    products[numberItems.product_id[0]] = {
                        id: numberItems.product_id[0],
                        count: 0
                    }
                    self.promotion_combo_product.push({
                        promotion_id: self.promotionIds['number_items'],
                        combo_id: numberItems.id,
                        product_id: numberItems.product_id[0],
                        price: numberItems.price ? numberItems.price : 0,
                        count: 0
                    })
                    self.allPromotions[self.promotionIds['number_items']][numberItems.id] = {
                        display_name: numberItems.display_name,
                        id: numberItems.id,
                        price: numberItems.price ? numberItems.price : 0,
                        buy_qty: numberItems.buy_qty,
                        offer_qty: numberItems.offer_qty,
                        promotion_id: numberItems.promotion_id[0],
                        promotion_name: numberItems.promotion_id[1],
                        type: 'number_items',
                        count: 0,
                        product_ids: products,
                        products: [numberItems.product_id[0]]
                    }
                    // } else {
                    //     self.allPromotions[self.promotionIds['number_items']][numberItems.id] = numberItems
                    // }
                });
            }
        }
    }, {
        model: 'pos.promotion.discount.specified.item',
        fields: [],
        condition: function (self) {
            return self.config.promotion;
        },
        domain: function (self) {
            return [
                ['promotion_id', 'in', self.promotion_ids]
            ]
        },
        context: {
            'pos': true
        },
        loaded: function (self, discount_specified_item) {
            console.log("pos.promotion.discount.specified.item", self, discount_specified_item);
            if (!self.promotion_combo_product) {
                self.promotion_combo_product = [];
            }
            if (!self.promotionIds) {
                self.promotionIds = {};
            }
            if (!self.allPromotions) {
                self.allPromotions = {};
            }
            if (!(self.promotionsToApply && self.promotionsToApply.length)) {
                self.promotionsToApply = [];
            }
            if (discount_specified_item && discount_specified_item.length) {
                self.promotionIds['discount_specified_item'] = discount_specified_item[0].promotion_id[0];
                self.promotionIds['discount_specified_item[0].promotion_id[0]'] = 'discount_specified_item';
                self.allPromotions[self.promotionIds['discount_specified_item']] = {};
                discount_specified_item.map(discountSpecifiedItem => {
                    // if (!self.allPromotions[discountSpecifiedItem.promotion_id[0]]) {
                    let freeProduct = {
                        id: discountSpecifiedItem.product_id[0],
                        count: 0
                    }
                    let products = {};
                    discountSpecifiedItem.product_ids.map(data => {
                        products[data] = {
                            id: data,
                            count: 0
                        }
                        self.promotion_combo_product.push({
                            promotion_id: self.promotionIds['discount_specified_item'],
                            combo_id: discountSpecifiedItem.id,
                            product_id: data,
                            price: discountSpecifiedItem.price,
                            count: 0
                        })
                    });
                    self.promotion_combo_product.push({
                        promotion_id: self.promotionIds['discount_specified_item'],
                        combo_id: discountSpecifiedItem.id,
                        product_id: discountSpecifiedItem.product_id[0],
                        price: discountSpecifiedItem.price ? discountSpecifiedItem.price : 0,
                        count: 0
                    })
                    self.allPromotions[self.promotionIds['discount_specified_item']][discountSpecifiedItem.id] = {
                        display_name: discountSpecifiedItem.display_name,
                        id: discountSpecifiedItem.id,
                        promotion_id: discountSpecifiedItem.promotion_id[0],
                        promotion_name: discountSpecifiedItem.promotion_id[1],
                        type: 'discount_specified_item',
                        price: discountSpecifiedItem.price ? discountSpecifiedItem.price : 0,
                        count: 0,
                        product_ids: products,
                        freeProduct: freeProduct,
                        products: discountSpecifiedItem.product_ids
                    }
                    // } else {
                    //     self.allPromotions[self.promotionIds['discount_specified_item']][discountSpecifiedItem.id] = discountSpecifiedItem
                    // }
                });
            }
        }
    }]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        // initialize: function (attributes, options) {
        //     var self = this;
        //     var res = _super_order.initialize.apply(this, arguments);
        //     setInterval(function () {
        //         self.auto_build_promotion();
        //         console.log('auto build promotion')
        //     }, 1000);
        //     return res;
        // },
        // auto_build_promotion: function () {
        //     if (!this.pos.building_promotion || this.pos.building_promotion == false) {
        //         var order = this.pos.get('selectedOrder');
        //         if (order && order.orderlines && order.orderlines.length && this.pos.config.promotion == true && this.pos.config.promotion_ids.length) {
        //             this.pos.building_promotion = true;
        //             order.compute_promotion()
        //             this.pos.building_promotion = false;
        //         }
        //     }
        // },
        get_total_without_promotion_and_tax: function () {
            console.log('get_total_without_promotion_and_tax');

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
            console.log('compute_promotion');
            var order = this;
            var lines = order.orderlines.models; // remove old lines applied promotion by total order
            if (lines.length) {
                lines.filter(line => line.promotion == true).forEach(line => {
                    return order.remove_orderline(line);
                })
            }
            var promotions = this.pos.promotions
            if (promotions && promotions.length) {
                if (promotions[0].product_id && promotions[0].product_id.length) {
                    this.pos.promotionServiceProduct = this.pos.db.get_product_by_id(promotions[0].product_id[0]);
                }
                if (order.orderlines.length) {
                    for (var i = 0; i < promotions.length; i++) {
                        var type = promotions[i].type
                        if (type == '1_discount_total_order') {
                            order.compute_discount_total_order(promotions[i]);
                        }
                        // discount by category
                        if (type == '2_value_reduction_on_goods_total') {
                            order.compute_value_reduction_on_goods_total(promotions[i]);
                        }
                    }
                    // discount filter by total of current order
                    // discount by quantity of product 3_discount_by_quantity_of_product
                    // if (type == '3_specified_goods_total' || type == '3_specified_goods_total' || type == '3_specified_goods_total') {
                    order.compute_all_promotions_related_to_product();
                    // }
                    // discount by pack
                    // if (type == '4_pack_discount') {
                    //     order.compute_pack_discount(promotions[i]);
                    // }
                    // // free items filter by pack
                    // if (type == '5_pack_free_gift') {
                    //     order.compute_pack_free_gift(promotions[i]);
                    // }
                    // // re-build price filter by quantity of product
                    // if (type == '6_price_filter_quantity') {
                    //     order.compute_price_filter_quantity(promotions[i]);
                    // }
                }
            }
        },
        export_for_printing: function () {
            console.log('export_for_printing');

            var res = _super_order.export_for_printing.apply(this, arguments);
            if (this.promotion_amount) {
                res.promotion_amount = this.promotion_amount;
            }
            return res
        },
        export_as_JSON: function () {
            console.log('export_as_JSON');

            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.promotion_amount) {
                json.promotion_amount = this.promotion_amount;
            }
            return json
        },
        product_quantity_by_product_id: function () {
            console.log('product_quantity_by_product_id');

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
        // 1. check current order can apply discount by total order
        checking_apply_total_order: function (promotion, type = '') {
            console.log('checking_apply_total_order');
            var discount_lines;
            switch (type) {
                case 'discount':
                    discount_lines = this.pos.promotion_discount_order_by_promotion_id[promotion.id];
                    break;
                case 'reduction':
                    discount_lines = this.pos.promotion_reduction_order_by_promotion_id[promotion.id];
                    break;

                default:
                    break;
            }
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
        // 3. check condition for apply discount by quantity product
        checking_apply_specified_goods_promotion_id: function () {
            console.log('checking_apply_specified_goods_promotion_id');

            this.pos.promotion_combo_product_gb_product_id = this.pos.promotion_combo_product.groupBy('product_id');
            // var can_apply = false;
            var promotions = {};
            promotions = this.pos.allPromotions;
            var product_quantity_by_product_id = this.product_quantity_by_product_id();
            // for (product_id in product_quantity_by_product_id) {
            promotions.apply = false;
            for (promotionId in promotions) {
                if (parseInt(promotionId)) {
                    combos = promotions[promotionId];
                    combos.apply = false; // promotion
                    for (comboId in combos) {
                        if (parseInt(comboId)) {
                            combo = combos[comboId];
                            combo.combo_ids = [];
                            combo.apply = true; // combo
                            var prouductCounts = [];
                            for (productId in combo.product_ids) {
                                if (parseInt(productId)) {
                                    product = combo.product_ids[productId];
                                    if (
                                        this.pos.promotion_combo_product_gb_product_id &&
                                        this.pos.promotion_combo_product_gb_product_id[productId] &&
                                        this.pos.promotion_combo_product_gb_product_id[productId].length > 1
                                    ) {
                                        this.pos.promotion_combo_product_gb_product_id[productId].map(data => {
                                            if (data.combo_id != parseInt(comboId) || data.promotion_id != parseInt(promotionId)) {
                                                combo.combo_ids.push(data);
                                            }
                                        });
                                    }
                                    switch (combo.type) {
                                        case 'specified_goods':
                                            // product = products[productId];
                                            // if (productId == product_id) {
                                            if (product_quantity_by_product_id[productId]) {
                                                product.count = product_quantity_by_product_id[productId];
                                                prouductCounts.push(product.count)
                                            } else {
                                                product.count = 0;
                                                prouductCounts.push(product.count)
                                                combo.apply = false;
                                                // combos.apply = false;
                                                // promotions.apply = true;
                                            }
                                            // }
                                            break;

                                        case 'number_items':
                                            if (product_quantity_by_product_id[productId] > combo.buy_qty) {
                                                product.count = product_quantity_by_product_id[productId];
                                                prouductCounts = Math.trunc(product_quantity_by_product_id[productId] / combo.buy_qty);
                                                // prouductCounts.push(product.count)
                                            } else {
                                                product.count = 0;
                                                prouductCounts = 0;
                                                // prouductCounts.push(product.count)
                                                combo.apply = false;
                                                // combos.apply = false;
                                                // promotions.apply = true;
                                            }
                                            break;

                                        case 'discount_specified_item':
                                            if (product_quantity_by_product_id[productId]) {
                                                product.count = product_quantity_by_product_id[productId];
                                                prouductCounts.push(product.count)
                                            } else {
                                                product.count = 0;
                                                prouductCounts.push(product.count)
                                                combo.apply = false;
                                                // combos.apply = false;
                                                // promotions.apply = true;
                                            }
                                            break;

                                        default:
                                            break;
                                    }
                                }
                            }

                            switch (combo.type) {
                                case 'specified_goods':
                                    combo.count = prouductCounts.min();

                                    break;

                                case 'number_items':
                                    combo.count = prouductCounts;

                                    break;

                                case 'discount_specified_item':
                                    if (product_quantity_by_product_id[combo.freeProduct.id]) {
                                        combo.freeProduct.count = product_quantity_by_product_id[combo.freeProduct.id];
                                    } else {
                                        combo.freeProduct.count = 0;
                                        combo.apply = false;
                                        // combos.apply = false;
                                        // promotions.apply = true;
                                    }
                                    combo.count = prouductCounts.min();

                                    break;

                                default:
                                    break;
                            }
                            combos.apply = combos.apply || combo.apply;
                        }
                    }
                    promotions.apply = promotions.apply || combos.apply;
                    // if (combos.apply) {
                    //     promotions.apply = true;
                    // }
                }
            }

            // var rules_by_product_id = promotionSpecifiedGoods[product_id];
            // if (rules_by_product_id) {
            //     for (var i = 0; i < rules_by_product_id.length; i++) {
            //         var rule = rules_by_product_id[i];
            //         if (rule && product_quantity_by_product_id[product_id] >= rule.quantity) {
            //             can_apply = true;
            //         }
            //     }
            // }

            // }
            console.log(promotions);
            return promotions.apply;
        },

        // 1. compute discount filter by total order
        compute_discount_total_order: function (promotion) {
            console.log('compute_discount_total_order');

            var discount_line_tmp = this.checking_apply_total_order(promotion, 'discount')

            if (discount_line_tmp == null) {
                return;
            }
            var total_order = this.get_total_without_promotion_and_tax();
            if (discount_line_tmp && total_order > 0) {
                var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                var price = (-total_order / 100 * discount_line_tmp.discount).toFixed(2);
                if (product && price != 0) {
                    var options = {};
                    options.promotion_discount_total_order = true;
                    options.promotion = true;
                    options.promotion_reason = 'discount ' + discount_line_tmp.discount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_amount;
                    this.add_promotion(this.pos.promotionServiceProduct, price, 1, options)
                }
            }
        },
        // 2. compute reduction filter by product categories
        compute_value_reduction_on_goods_total: function (promotion) {
            console.log('compute_value_reduction_on_goods_total', promotion);


            var reduction_line_tmp = this.checking_apply_total_order(promotion, 'reduction')

            if (reduction_line_tmp == null) {
                return;
            }
            var total_order = this.get_total_without_promotion_and_tax();
            if (reduction_line_tmp && total_order > 0) {
                var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                var price = -reduction_line_tmp.value.toFixed(2);
                if (product && price != 0) {
                    var options = {};
                    options.promotion_value_reduction_on_goods_total = true;
                    options.promotion = true;
                    options.promotion_reason = 'reduction ' + reduction_line_tmp.value + ' $ ' + ' when total order greater or equal ' + reduction_line_tmp.minimum_amount;
                    this.add_promotion(this.pos.promotionServiceProduct, price, 1, options)
                }
            }
        },
        // 3. compute discount filter by quantity of product
        compute_all_promotions_related_to_product: function () {
            this.pos.promotionsToApply = [];
            console.log('compute_all_promotions_related_to_product');
            // var specifiedGoods = this.pos.allPromotions[this.pos.promotionIds['specified_goods']];
            // var specifiedGoods = this.pos.allPromotions[this.pos.promotionIds['specified_goods']];
            // var specifiedGoods = this.pos.allPromotions[this.pos.promotionIds['specified_goods']];
            // if (specifiedGoods.apply == false) {
            //     return;
            // }

            for (promotionId in this.pos.allPromotions) {
                singlePromotions = this.pos.allPromotions[promotionId];
                for (singlePromotionKey in singlePromotions) {
                    singlePromotion = singlePromotions[singlePromotionKey]
                    if (singlePromotion.apply) {
                        switch (singlePromotion.type) {
                            case 'specified_goods':
                                singlePromotion.totalProductPrice = 0;
                                singlePromotion.productsDetails = singlePromotion.products.map(product => {
                                    product = this.pos.db.get_product_by_id(product);
                                    singlePromotion.totalProductPrice += product.price;
                                    return product;
                                });
                                singlePromotion.productNames = singlePromotion.productsDetails.map(productsDetail => productsDetail.display_name);
                                singlePromotion.reductionAmount = singlePromotion.price - singlePromotion.totalProductPrice;
                                singlePromotion['promotion_' + this.pos.promotionIds[promotionId]] = true;
                                this.pos.promotionsToApply.push(singlePromotion);

                                break;

                            case 'number_items':
                                singlePromotion.productsDetails = singlePromotion.products.map(product => {
                                    product = this.pos.db.get_product_by_id(product);
                                    singlePromotion.price = product.price * singlePromotion.offer_qty;
                                    return product;
                                });
                                singlePromotion.productNames = singlePromotion.productsDetails.map(productsDetail => productsDetail.display_name);
                                singlePromotion.reductionAmount = -singlePromotion.price;
                                singlePromotion['promotion_' + singlePromotion.type] = true;
                                this.pos.promotionsToApply.push(singlePromotion);
                                break;

                            case 'discount_specified_item':
                                singlePromotion.productsDetails = singlePromotion.products.map(product => this.pos.db.get_product_by_id(product));
                                singlePromotion.productNames = singlePromotion.productsDetails.map(productsDetail => productsDetail.display_name);
                                singlePromotion.freeProductsDetails = this.pos.db.get_product_by_id(singlePromotion.freeProduct.id);
                                singlePromotion.reductionAmount = freeProductsDetails.price;
                                singlePromotion['promotion_' + this.pos.promotionIds[promotionId]] = true;
                                this.pos.promotionsToApply.push(singlePromotion);

                                break;

                            default:
                                break;
                        }
                    }
                }
            }
            if (this.pos.promotionsToApply && this.pos.promotionsToApply.length) {
                var promotion_lines = [];
                this.pos.promotionsToApply.map(promoToApply => {
                    if (promoToApply.apply) {
                        promotion_lines.push(promoToApply);
                    }
                })
            } else {
                return;
            }


            // if (reduction_line_tmp == null) {
            //     return;
            // }
            var total_order = this.get_total_without_promotion_and_tax();
            if (promotion_lines && promotion_lines.length && total_order > 0) {
                promotion_lines.map(promotionLine => {

                    // var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                    this.pos.scrap._price = promotionLine.reductionAmount.toFixed(2)
                    this.pos.scrap._productNames = promotionLine.productNames.join(' ');
                    this.pos.scrap._reason = 'reduction ~~_price~~ $ for combo products ~~_productNames~~';
                    if (this.pos.scrap._price != 0) {
                        var options = promotionLine;
                        options.promotion = true;
                        options.promotion_reason = this.pos.scrap._reason.split('~~').map(data => {
                            console.log(
                                this.pos.scrap[data]
                            );
                            if (this.pos.scrap[data]) {
                                if (parseInt(this.pos.scrap[data])) {
                                    return Math.abs(this.pos.scrap[data]);
                                }
                                return this.pos.scrap[data];
                            } else {
                                return data
                            }
                        }).join(' ');
                        // options.promotion_reason = 'reduction ' + price + ' $ for combo products ' + promotionLine.productNames.join(' ');
                        this.add_promotion(this.pos.promotionServiceProduct, this.pos.scrap._price, promotionLine.count, options)
                    }
                })
            }



            /* var quantity_by_product_id = {}
            var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
            var i = 0;
            var lines = this.orderlines.models;
            while (i < lines.length) {
                var line = lines[i];
                if (line.promotion_specified_goods && line.promotion_specified_goods == true) {
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
                // specifiedGoods.product_id
                var promotion_lines = this.pos.promotion_combo_product_gb_product_id[product_id];
                // var promotion_lines = this.pos.promotion_quantity_by_product_id[product_id];
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
                        if (lines[x].promotion_specified_goods) {
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
                    options.promotion_specified_goods = true;
                    options.promotion = true;
                    options.promotion_reason = ' discount ' + promotion_line.discount + ' % when ' + promotion_line.product_id[1] + ' have quantity greater or equal ' + promotion_line.quantity;
                    this.add_promotion(product, price, 1, options)
                }
            } */
        },

        // add promotion to current order
        add_promotion: function (product, price, quantity, options) {
            console.log('add_promotion');

            var line = new models.Orderline({}, {
                pos: this.pos,
                order: this,
                product: product
            });
            if (options.promotion) {
                line.promotion = options.promotion;
            }
            if (options.promotion_reason) {
                line.promotion_reason = options.promotion_reason;
            }
            if (options.promotion_discount_total_order) {
                line.promotion_discount_total_order = options.promotion_discount_total_order;
            }
            if (options.promotion_value_reduction_on_goods_total) {
                line.promotion_value_reduction_on_goods_total = options.promotion_value_reduction_on_goods_total;
            }
            if (options.promotion_specified_goods) {
                line.promotion_specified_goods = options.promotion_specified_goods;
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
            console.log('current_order_can_apply_promotion');
            var check_all_promotions_related_to_product = false;
            var can_apply = null;
            for (var i = 0; i < this.pos.promotions.length; i++) {
                var promotion = this.pos.promotions[i];
                if (promotion['type'] == '1_discount_total_order' && this.checking_apply_total_order(promotion)) {
                    can_apply = true;
                } else if (promotion['type'] == '2_value_reduction_on_goods_total' && this.checking_apply_total_order(promotion)) {
                    can_apply = true;
                } else if (
                    promotion['type'] == '3_specified_goods_total' ||
                    promotion['type'] == '4_number_items_price' ||
                    promotion['type'] == '5_discount_specified_item'
                ) {
                    check_all_promotions_related_to_product = true;
                }
            }
            if (check_all_promotions_related_to_product && this.checking_apply_specified_goods_promotion_id()) {
                can_apply = true;
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
            if (json.promotion_value_reduction_on_goods_total) {
                this.promotion_value_reduction_on_goods_total = json.promotion_value_reduction_on_goods_total;
            }
            if (json.promotion_specified_goods) {
                this.promotion_specified_goods = json.promotion_specified_goods;
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
            if (json.sales_person) {
                this.sales_person = json.sales_person
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
            if (this.promotion_value_reduction_on_goods_total) {
                json.promotion_value_reduction_on_goods_total = this.promotion_value_reduction_on_goods_total;
            }
            if (this.promotion_specified_goods) {
                json.promotion_specified_goods = this.promotion_specified_goods;
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
            if (this.sales_person) {
                json.sales_person = this.sales_person
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
            var res = _super_orderline.can_be_merged_with.apply(this, arguments);
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
            console.log('button_promotion button_click');

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
            console.log('define_action_button');
            return this.pos.config.promotion == true && this.pos.promotion_ids.length && this.pos.promotion_ids.length >= 1;
        },
    });
});