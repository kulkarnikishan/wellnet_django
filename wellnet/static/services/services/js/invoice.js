(function ($) {
    function showHideExpectedDate(checked) {
        if (checked == 'checked') {
            $("div.field-expected_delivery_date").hide();
        } else {
            $("div.field-expected_delivery_date").show();
        }
    }

    function showHideGST(checked) {
        if (checked == 'checked') {
            //Hiding Percentage bases checking Is_IGST_format or not
            $('table thead tr th').each(function (index, ele) {
                if ($(ele).text().trim() == "CGST In %" || $(ele).text().trim() == "SGST In %") {
                    $(ele).hide();
                    $('.field-CGST_percentage').hide();
                    $('.field-IGST_percentage').show();
                    $('.field-SGST_percentage').hide();
                } else {
                    $(ele).show();
                }
            });
            $("div.field-CGST_amount").hide();
            $("div.field-SGST_amount").hide();
            $("div.field-IGST_amount").show();
        } else {
            $('table thead tr th').each(function (index, ele) {
                if ($(ele).text().trim() == "IGST In %") {
                    $(ele).hide();
                    $('.field-IGST_percentage').hide();
                    $('.field-SGST_percentage').show();
                    $('.field-CGST_percentage').show();
                } else {
                    $(ele).show();
                }
            });
            $("div.field-CGST_amount").show();
            $("div.field-SGST_amount").show();
            $("div.field-IGST_amount").hide();

        }
    }

    function showHidePaymentDetails(val) {
        switch (val) {
            case '1':
            case '2':
                $("#fieldset-2").show();
                $("div.field-utr_number").hide();
                $("div.field-transfer_date").hide();
                $("div.field-cheque_dd_number").show();
                $("div.field-cheque_dd_date").show();
                $("div.field-bank_name").show();
                $("div.field-bank_branch").show();
                $("div.field-realisation_date").show();
                break;
            case '3':
                $("#fieldset-2").show();
                $("div.field-cheque_dd_number").hide();
                $("div.field-cheque_dd_date").hide();
                $("div.field-utr_number").show();
                $("div.field-transfer_date").show();
                $("div.field-bank_name").show();
                $("div.field-bank_branch").show();
                $("div.field-realisation_date").show();
                break;
            case '4':
            case '5':
                $("#fieldset-2").show();
                $("div.field-cheque_dd_number").hide();
                $("div.field-cheque_dd_date").hide();
                $("div.field-utr_number").hide();
                $("div.field-bank_name").hide();
                $("div.field-bank_branch").hide();
                $("div.field-transfer_date").show();
                $("div.field-realisation_date").hide();
                break;
        }
    }

    function getTotalAmount(showAlert) {
        var products = [];
        var quantities = [];
        var base_prices = [];
        var ids = [];
        var tax_ids = [];
        $("select[id^='id_productquantity_set-']").each(function (index, select) {
            var product = $(this).val();
            if (product != undefined && product != '') {
                var quantity = $(this).parent().parent().parent().find("input[name$='quantity']").val();
                var base_price = $(this).parent().parent().parent().find("input[name$='base_price']").val();
                if (quantity != undefined && quantity != '') {
                    products.push(product);
                    quantities.push(quantity);
                    ids.push("#id_productquantity_set-" + index + "-gross_amount");
                    tax_ids.push("#id_productquantity_set-" + index + "-CGST_percentage");
                    tax_ids.push("#id_productquantity_set-" + index + "-SGST_percentage");
                    tax_ids.push("#id_productquantity_set-" + index + "-IGST_percentage");

                } else {
                    $("#id_productquantity_set-" + index + "-gross_amount").val('');
                }
                if (base_price != undefined && base_price != '') {
                    base_prices.push(base_price)
                } else {
                    base_prices.push(0);
                    $("#id_productquantity_set-" + index + "-base_price").val('');
                }
            }
        });
        var createdFor = $("#id_createdFor");
        var createdForVal = createdFor.length != 0 ?
            createdFor.val() != undefined && createdFor.val() != "" ?
                createdFor.val() : 0 : 0;
        if (createdFor.length != 0 && createdForVal == 0) {
            if (showAlert) {
                alert("Select Created For field to get amount.");
            }
        } else {
            if (products.length != 0) {
                $.ajax({
                    data: {
                        'products': products,
                        'quantities': quantities,
                        'base_prices': base_prices,
                        'ids': ids,
                        'tax_ids': tax_ids,
                        'createdFor': createdForVal
                    },
                    url: "/custom/services/getAmount",
                    success: function (response) {
                        $("#id_SGST_amount").val(response["SGST_amount"]);
                        $("#id_IGST_amount").val(response["IGST_amount"]);
                        $("#id_CGST_amount").val(response["CGST_amount"]);
                        if ($("#id_is_IGST").attr('checked')) {
                            $("#id_amount").val(response["igst_total_amt"]);
                        } else {
                            $("#id_amount").val(response["amount"]);
                        }
                        $("#id_gross_amount").val(response["gross"]);
                        $("#id_IGST_percentage ").val(response["igst"]);
                        $("#id_SGST_percentage ").val(response["sgst"]);
                        $("#id_CGST_percentage ").val(response["cgst"]);
                        amounts = response["product_amounts"];
                        tax_amt_array = response["tax_amt_array"];
                        $.each(amounts, function (index, value) {
                            $.each(value, function (k, v) {
                                $(k).val(v);
                            });
                        });
                        $.each(tax_amt_array, function (index, value) {
                            $.each(value, function (k, v) {
                                $(k).val(v);
                            });
                        });
                    }
                });
            } else {
                $("#id_SGST_amount").val('');
                $("#id_CGST_amount").val('');
                $("#id_IGST_amount").val('');
                $("#id_amount").val('');
                $("#id_gross_amount").val('');

            }
        }
    }

    function showHideDeliveryInfo(value) {
        switch (value) {
            case '1':
                if (window.location.pathname.substring(window.location.pathname.lastIndexOf('/') - 3) == 'add/') {
                    $("#fieldset-3").hide();
                } else {
                    $("#fieldset-3").show();
                }
                $("div.field-courier_company_name").show();
                $("div.field-pod_number").show();
                $("div.field-person_name").hide();
                $("div.field-contact_number").hide();
                break;
            case '2':
            case '3':
                $("#fieldset-3").show();
                $("div.field-courier_company_name").hide();
                $("div.field-pod_number").hide();
                $("div.field-person_name").show();
                $("div.field-contact_number").show();
                break;
            default:
                $("#fieldset-3").hide();
                break;
        }
    }

    function wordCount(val) {
        var wom = val.match(/\S+/g);
        return {
            charactersNoSpaces: val.replace(/\s+/g, '').length,
            characters: val.length,
            words: wom ? wom.length : 0,
            lines: val.split(/\r*\n/).length
        };
    }

    function check_value_for_select() {
        var selected = $("select#id_createdFor option:selected").html();
        if (selected != undefined && selected != '') {
            if ($("#select2-id_createdFor-container").html() == "") {
                $("#select2-id_createdFor-container").html(selected);
            }
        }
    }

    function enable_edit_function() {
        var edit = $("#change_id_createdFor");
        var customer_pk = $("select#id_createdFor").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }

    $(document).ready(function () {
        $("#fieldset-1").before($("#productquantity_set-group"));
        $("#productquantity_set-group").before($("#fieldset-5"));
        $("#fieldset-2").hide();
        // $("#fieldset-2 .control-label label").addClass("required");
        if ($("#id_payment_type").val() != undefined && $("#id_payment_type").val() != '') {
            showHidePaymentDetails($("#id_payment_type").val());
        }
        $("#id_payment_type").on('change', function () {
            if ($(this).val() != undefined && $(this).val() != '') {
                showHidePaymentDetails($(this).val());
            }
        });
        $("select[id^='id_productquantity_set-']").on('change', function () {
            getTotalAmount(true);
        });
        $("select[id^='id_createdFor']").on('change', function () {
            getTotalAmount(false);
            enable_edit_function();
        });
        $("input[id^='id_productquantity_set-'][type=text]").on('blur', function () {
            getTotalAmount(true);
        });
        $("input[id^='id_productquantity_set-'][type=number]").on('change', function () {
            getTotalAmount(true);
        });
        $("input[id^='id_productquantity_set-'][type=checkbox]").on('click', function () {
            var qtyId = $(this).attr("id").replace("-DELETE", "-quantity");
            var base_priceId = $(this).attr("id").replace("-DELETE", "-base_price");
            var qty = $("#" + qtyId);
            if ($(this).attr('checked')) {
                qty.attr('data-value', qty.val());
                qty.val(0);
            } else {
                qty.val(qty.attr('data-value'));
            }
            var base_price = $("#" + base_priceId);
            if ($(this).attr('checked')) {
                base_price.attr('data-value', base_price.val());
                base_price.val(0);
            } else {
                base_price.val(base_price.attr('data-value'));
            }
            getTotalAmount(true);
        });
        getTotalAmount(false)
        $("tr[id^='productquantity_set'] td.original p").each(function (index, object) {
            $(this).html($(this).html() + "#" + (index + 1));
        });
        $("ul.errorlist > li").addClass("text-danger");
        $("#id_is_immediate").on('click', function () {
            showHideExpectedDate($(this).attr('checked'));
        });
        showHideExpectedDate($("#id_is_immediate").attr('checked'));
        setTimeout(function () {
            if ($("#id_order_delivery_date").attr("readonly") == "readonly") {
                $("#id_order_delivery_date").parent().find("span.datetimeshortcuts").remove();
            }
        }, 1);
        if (window.location.pathname.substring(window.location.pathname.lastIndexOf('/') - 3) == 'add/') {
            $("div.field-order_delivery_date").remove();
            $("div.field-courier_company_name").remove();
            $("div.field-pod_number").remove();
            $("#fieldset-6").remove();
        }
        $("#id_order_delivery_type").on('change', function () {
            showHideDeliveryInfo($(this).val());
        });
        $("#id_is_IGST").on('click', function () {
            showHideGST($(this).attr('checked'));
            getTotalAmount()
        });
        showHideGST($("#id_is_IGST").attr('checked'));
        showHideDeliveryInfo($("#id_order_delivery_type").val());
        if ($("#id_cancel_reason").length != 0) {
            $("#id_cancel_reason").parent().append("<label id=\"word_counter\" style=\"float: right;\">"
                + wordCount($("#id_cancel_reason").val()).characters + "/255</label>");
            var result = $("#word_counter")
            $("#id_cancel_reason").on("input", function () {
                var v = wordCount($(this).val());
                result.html(v.characters + '/255')
            });
        }
        $('select#id_createdFor').bind("DOMSubtreeModified", check_value_for_select);
        $('span.glyphicon-pencil').hide()
        $('span.glyphicon-plus').hide()

    });
}(this.jQuery));
