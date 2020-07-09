(function ($) {
	function showHidePaymentDetails(val) {
		switch(val) {
			case '1':
			case '2':
				$("#fieldset-2").show();
				$("div.field-utr_number").hide();
				$("div.field-transfer_date").hide();
				$("div.field-cheque_dd_number").show();
				$("div.field-cheque_dd_date").show();
				break;
			case '3':
				$("#fieldset-2").show();
				$("div.field-cheque_dd_number").hide();
				$("div.field-cheque_dd_date").hide();
				$("div.field-utr_number").show();
				$("div.field-transfer_date").show();
				break;
			case '4':
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
	function showHideSegmentOtherDetails(val) {
		if (val != undefined && val != '') {
			switch(val) {
				case '1':
					$("div.field-company_name").hide();
					$("div.field-building_name").show();
					$("div.field-pin_code").show();
					$("div.field-vehicle_category").hide();
					$("div.field-year_of_manufacture").hide();
					$("div.field-vehicle_name").hide();
					$("div.field-vehicle_registration_no").hide();
					break;
				case '2':
				case '3':
				case '4':
					$("div.field-company_name").show();
					$("div.field-building_name").show();
					$("div.field-pin_code").show();
					$("div.field-vehicle_category").hide();
					$("div.field-year_of_manufacture").hide();
					$("div.field-vehicle_name").hide();
					$("div.field-vehicle_registration_no").hide();
					break;
				case '5':
					$("div.field-company_name").hide();
					$("div.field-building_name").hide();
					$("div.field-pin_code").hide();
					$("div.field-vehicle_category").show();
					$("div.field-year_of_manufacture").show();
					$("div.field-vehicle_name").show();
					$("div.field-vehicle_registration_no").show();
					break;
				default:
					$("div.field-company_name").hide();
					$("div.field-building_name").hide();
					$("div.field-pin_code").hide();
					$("div.field-vehicle_category").hide();
					$("div.field-year_of_manufacture").hide();
					$("div.field-vehicle_name").hide();
					$("div.field-vehicle_registration_no").hide();
			}
		}
	}
	var showHideSegments = false;
	var selectedProducts = [0, 0];
	function showHideSegmentSection() {
	    $("select[id^='id_customerproductquantity_set-']").each(
	        function(index, select) {
                val = $(select).val();
                if (val != undefined && val != '') {
                    selectedProducts[index] = val;
                }
	    });
	    if ($.inArray("1", selectedProducts) != -1) {
	        $("div.field-segment").show();
	    } else {
	        $("#id_segment").select2("val", "");
	        $("div.field-segment").hide();
	        $("#id_company_name").val("");
	        $("#id_building_name").val("");
	        $("#id_pin_code").val("");
	        $("#id_vehicle_category").select2("val", "");
	        $("#id_vehicle_name").val("");
	        $("#id_vehicle_registration_no").val("");
	        $("#id_year_of_manufacture").val("");
	        $("div.field-company_name").hide();
                $("div.field-building_name").hide();
                $("div.field-pin_code").hide();
                $("div.field-vehicle_category").hide();
                $("div.field-year_of_manufacture").hide();
                $("div.field-vehicle_name").hide();
                $("div.field-vehicle_registration_no").hide();
	    }
	}
	function getTotalAmount(calledFrom) {
		var products = [];
		var quantities = [];
		var totals = [];
		var ids = [];
		var segment = $("#id_segment").val();
		segment = segment == undefined || segment == '' ? 0 : segment;
		$("select[id^='id_customerproductquantity_set-']").each(function (index, select){
			var product = $(this).val();
			if(product != undefined && product != '') {
				var quantity = $(this).parent().parent().parent().find("input[name$='quantity']").val();
				if (quantity != undefined && quantity != '') {
				    if (product == 1 && segment == 0) {
				        // do not add product and quantity
                                        $("#id_customerproductquantity_set-"+index+"-gross_amount").val('');
					if (calledFrom) {
					    alert("Select Customer Category to get the amount");
					}
				    } else {
					var total = $(this).parent().parent().parent().find("input[name$='gross_amount']").val();
					if (total == undefined || total == '') {
					    total = -1
					}
					products.push(product);
					quantities.push(quantity);
					totals.push(total);
					ids.push("#id_customerproductquantity_set-"+index+"-gross_amount");
				    }
				}
			}
		});
		
		if (products.length != 0) {
			var vehicle_category = $("#id_vehicle_category").val();
			vehicle_category = vehicle_category == undefined || vehicle_category == '' ? 0 : vehicle_category;
			if (segment == 5 && vehicle_category == 0) {
			    if (calledFrom) {
                    alert("Select Vehicle Category to get the amount");
                }
			} else {
			    $.ajax({
				data: {'products': products, 'quantities': quantities, 'segment': segment, 'vehicle_category': vehicle_category,
				    'totals': totals, 'ids': ids},
				url: "/custom/services/getAmountForCustomer",
				success: function(response) {
					$("#id_service_tax").val(response["service_tax"]);
					$("#id_vat").val(response["vat"]);
					$("#id_amount").val(response["amount"]);
					$("#id_gross_amount").val(response["gross"]);
					amounts = response["product_amounts"];
					$.each(amounts, function(index, value) {
					    $.each(value, function(k, v){
					        $(k).val(v);
					    });
					});
					if (response["error"] != undefined) {
						alert(response["error"])
					}
				}
			});
			}
		} else {
		    $("#id_service_tax").val('');
            $("#id_vat").val('');
            $("#id_amount").val('');
		}
	}
	function check_value_for_select() {
        var selected = $("select#id_user option:selected").html();
        if (selected != undefined && selected != '') {
            if($("#select2-id_user-container").html() == "") {
                $("#select2-id_user-container").html(selected);
            }
        }
    }
    function enable_edit_function() {
        var edit = $("#change_id_user");
        var customer_pk = $("select#id_user").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }
	$(document).ready(function(){
		$("#fieldset-4").before($("#customerproductquantity_set-group"));
		$("#fieldset-2").hide();
		var init_segment = $("#id_segments").val();
		init_segment = init_segment != undefined && init_segment != '' ? init_segment : 'hide';
		showHideSegmentOtherDetails(init_segment);
		$("#fieldset-2 .control-label label").addClass("required");
		$("#fieldset-3 .control-label label").addClass("required");
		if ($("#id_payment_type").val() != undefined && $("#id_payment_type").val() != '') {
			showHidePaymentDetails($("#id_payment_type").val());
		}
		$("#id_payment_type").on('change', function() {
			if ($(this).val() != undefined && $(this).val() != '') {
				showHidePaymentDetails($(this).val());
			}
		});
		$("select[id^='id_customerproductquantity_set-']").on('change', function (){
			getTotalAmount(true);
			showHideSegmentSection();
		});
		$("#id_segment").on('change', function (){
			getTotalAmount(false);
			showHideSegmentOtherDetails($(this).val());
		});
		$("#id_vehicle_category").on('change', function (){
			getTotalAmount(false);
		});
		$("input[id^='id_customerproductquantity_set-'][type=text]").on('blur', function (){
			getTotalAmount(true);
		});
		$("input[id^='id_customerproductquantity_set-'][type=checkbox]").on('click', function (){
			var qtyId = $(this).attr("id").replace("-DELETE", "-quantity");
			var qty = $("#"+qtyId);
			if($(this).attr('checked')) {
				qty.attr('data-value', qty.val());
				qty.val(0);
			} else {
				qty.val(qty.attr('data-value'));
			}
			getTotalAmount(true);
		});
		$("tr[id^='customerproductquantity_set'] td.original p").each(function(index, object){
			$(this).html($(this).html() + "#"+ (index+1));
		});
		$("ul.errorlist > li").addClass("text-danger");
		showHideSegmentOtherDetails($("#id_segment").val());
		$('select#id_user').bind("DOMSubtreeModified", check_value_for_select);
		$("select#id_user").on('change', enable_edit_function);
	});
}(this.jQuery));
