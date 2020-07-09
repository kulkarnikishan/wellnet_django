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
                }else{
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
                }else{
                   $(ele).show();
                }
            });
            $("div.field-CGST_amount").show();
            $("div.field-SGST_amount").show();
            $("div.field-IGST_amount").hide();

        }
    }

    function getTotalAmount(showAlert) {
        var products = [];
        var quantities = [];
        var base_prices = [];
        var ids = [];
        var tax_ids = [];
        $("select[id^='id_proformaproductquantity_set-']").each(function (index, select) {
            var product = $(this).val();
            if (product != undefined && product != '') {
                var quantity = $(this).parent().parent().parent().find("input[name$='quantity']").val();
                var base_price = $(this).parent().parent().parent().find("input[name$='base_price']").val();
                if (quantity != undefined && quantity != '') {
                    products.push(product);
                    quantities.push(quantity);
                    ids.push("#id_proformaproductquantity_set-" + index + "-gross_amount");
                    tax_ids.push("#id_proformaproductquantity_set-" + index + "-CGST_percentage");
                    tax_ids.push("#id_proformaproductquantity_set-" + index + "-SGST_percentage");
                    tax_ids.push("#id_proformaproductquantity_set-" + index + "-IGST_percentage");

                } else {
                    $("#id_proformaproductquantity_set-" + index + "-gross_amount").val('');
                }
                if (base_price != undefined && base_price != '') {
                    base_prices.push(base_price)
                } else {
                    base_prices.push(0);
                    $("#id_proformaproductquantity_set-" + index + "-base_price").val('');
                }
            }
        });
        var createdFor = $("#id_created_For");
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
                        'createdFor': createdForVal},
                    url: "/custom/services/getAmount",
                    success: function (response) {
                        $("#id_SGST_amount").val(response["SGST_amount"]);
                        $("#id_IGST_amount").val(response["IGST_amount"]);
                        $("#id_CGST_amount").val(response["CGST_amount"]);
                         if($("#id_is_IGST").attr('checked')){
                            $("#id_amount").val(response["igst_total_amt"]);
                        }else{
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
        $("#fieldset-1").before($("#proformaproductquantity_set-group"));
        $("#proformaproductquantity_set-group").before($("#fieldset-3"));

        // $("#fieldset-2 .control-label label").addClass("required");
        $("select[id^='id_proformaproductquantity_set-']").on('change', function () {
            getTotalAmount(true);
        });
        $("select[id^='id_createdFor']").on('change', function () {
            getTotalAmount(false);
            enable_edit_function();
        });
        $("input[id^='id_proformaproductquantity_set-'][type=text]").on('blur', function () {
            getTotalAmount(true);
        });
        $("input[id^='id_proformaproductquantity_set-'][type=number]").on('change', function () {
            getTotalAmount(true);
        });
        $("input[id^='id_proformaproductquantity_set-'][type=checkbox]").on('click', function () {
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
        getTotalAmount(false);
        $("tr[id^='proformaproductquantity_set'] td.original p").each(function (index, object) {
            $(this).html($(this).html() + "#" + (index + 1));
        });
        $("ul.errorlist > li").addClass("text-danger");

        $("#id_is_IGST").on('click', function () {
            showHideGST($(this).attr('checked'));
            getTotalAmount()
        });
        showHideGST($("#id_is_IGST").attr('checked'));
        $('select#id_createdFor').bind("DOMSubtreeModified", check_value_for_select);
         $('span.glyphicon-pencil').hide()
        $('span.glyphicon-plus').hide()

    });
}(this.jQuery));
