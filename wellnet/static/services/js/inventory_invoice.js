(function ($) {
	function showHidePaymentDetails(val) {
		switch(val) {
			case '1':
			case '2':
				$("#fieldset-3").show();
				$("div.field-utr_number").hide();
				$("div.field-transfer_date").hide();
				$("div.field-cheque_dd_number").show();
				$("div.field-cheque_dd_date").show();
				break;
			case '3':
				$("#fieldset-3").show();
				$("div.field-cheque_dd_number").hide();
				$("div.field-cheque_dd_date").hide();
				$("div.field-utr_number").show();
				$("div.field-transfer_date").show();
				break;
			case '4':
				$("#fieldset-3").hide();
				break;
		}
	}
	function showHideDiffPaymentDetails(val) {
		switch(val) {
			case '1':
			case '2':
				$("#fieldset-6").show();
				$("div.field-difference_utr_number").hide();
				$("div.field-difference_transfer_date").hide();
				$("div.field-difference_cheque_dd_number").show();
				$("div.field-difference_cheque_dd_date").show();
				break;
			case '3':
				$("#fieldset-6").show();
				$("div.field-difference_cheque_dd_number").hide();
				$("div.field-difference_cheque_dd_date").hide();
				$("div.field-difference_utr_number").show();
				$("div.field-difference_transfer_date").show();
				break;
			case '4':
				$("#fieldset-6").hide();
				break;
			default:
				$("#fieldset-6").hide();
				break;
		}
	}
	function checkGoodSold(check) {
		if(check) {
			$("div.field-goods_price").show();
			$("div.field-settlement_amount").hide();
			$("#id_settlement_amount").val("");
		} else {
			$("#fieldset-5").hide();
			$("#fieldset-6").hide();
			$("div.field-goods_price").hide();
			$("#id_goods_price").val("");
			$("div.field-settlement_amount").show();
		}
	}
	function getDifferenceAmount(val) {
		security = $("#id_security_deposite_amount").val();
		amt = $("#id_difference_amount");
		diff = security - val;
		if (diff != 0) {
			amt.val(Math.abs(diff));
			$("#fieldset-5").show();
			showHideDiffPaymentDetails($("#id_difference_payment_type").val());
		} else {
			amt.val(Math.abs(diff));
			$("#fieldset-5").hide();
			$("#fieldset-6").hide();
			reset_fieldset("#fieldset-5");
			reset_fieldset("#fieldset-6");
		}
	}
	function reset_fieldset(id) {
		$(id + " input[type=text]").val("");
	}
	function checkDiff() {
		amt = $("#id_difference_amount").val();
		if (amt != '' && Math.abs(amt) > 0) {
			$("#fieldset-5").show();
			showHideDiffPaymentDetails($("#id_difference_payment_type").val());
		}
	}
	function check_value_for_machine() {
        var selected = $("select#id_machine option:selected").html();
        if (selected != undefined && selected != '') {
            if($("#select2-id_machine-container").html() == "") {
                $("#select2-id_machine-container").html(selected);
            }
        }
    }
    function check_value_for_partner() {
        var selected = $("select#id_partner option:selected").html();
        if (selected != undefined && selected != '') {
            if($("#select2-id_partner-container").html() == "") {
                $("#select2-id_partner-container").html(selected);
            }
        }
    }
    function enable_edit_function_machine() {
        var edit = $("#change_id_machine");
        var customer_pk = $("select#id_machine").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }
    function enable_edit_function_partner() {
        var edit = $("#change_id_partner");
        var customer_pk = $("select#id_partner").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }
	$(document).ready(function(){
		$("#fieldset-3").hide();
		$("#fieldset-5").hide();
		$("#fieldset-6").hide();
		$("div.field-goods_price").hide();
		if ($("#id_payment_type").val() != undefined && $("#id_payment_type").val() != '') {
			showHidePaymentDetails($("#id_payment_type").val());
		}
		$("#id_payment_type").on('change', function() {
			if ($(this).val() != undefined && $(this).val() != '') {
				showHidePaymentDetails($(this).val());
			}
		});
		if ($("#id_difference_payment_type").val() != undefined && $("#id_difference_payment_type").val() != '') {
			showHideDiffPaymentDetails($("#id_difference_payment_type").val());
		}
		$("#id_difference_payment_type").on('change', function() {
			if ($(this).val() != undefined && $(this).val() != '') {
				showHideDiffPaymentDetails($(this).val());
			}
		});
		checkGoodSold($("#id_goods_sold").attr('checked'));
		$("#id_goods_sold").on('click', function (){
			checkGoodSold($(this).attr('checked'));
		});
		$("#id_goods_price").on('blur', function (){
			getDifferenceAmount($(this).val());
		});
		$("#id_settlement_amount").on('blur', function (){
			getDifferenceAmount($(this).val());
		});
		checkDiff();
		$('select#id_partner').bind("DOMSubtreeModified", check_value_for_partner);
		$('select#id_machine').bind("DOMSubtreeModified", check_value_for_machine);
		$("select#id_partner").on('change', enable_edit_function_partner);
		$("select#id_machine").on('change', enable_edit_function_machine);
	});
}(this.jQuery));
