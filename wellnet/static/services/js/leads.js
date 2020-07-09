(function ($) {
	function showHideMoreDetails(val) {
		if (val != undefined && val != '') {
			if (val == 9) {
				$("div.field-more_details").show();
			} else {
				$("div.field-more_details").hide();
			}
			if (val == 1 || val == 8 || val == 9) {
				$("div.field-next_appointment").show();
			} else {
				$("div.field-next_appointment").hide();
			}
			if (val >= 2 || val <= 6 || val == 9 || val == 8) {
				$("div.field-comments").show();
			} else {
				$("div.field-comments").hide();
			}
			if(val == 7) {
				$("#fieldset-5").show();
			} else {
				$("#fieldset-5").hide();
			}
		} else {
			$("div.field-more_details").hide();
			$("div.field-next_appointment").hide();
			$("div.field-comments").hide();
			$("#fieldset-5").hide();
		}
	}
	function mockCommentsSection() {
	    var comm = $("#id_comments").clone().attr('id', 'id_comments_cloned').attr('name', 'comments_cloned').val('');
	    $("#id_comments").parent().append(comm);
	    $("#id_comments").attr('readonly', 'true');
	    var date = new Date();
	    var initial = "";
	    if ($("#id_comments").val() != '') {
	        initial = $("#id_comments").val() + '\n' + date.toLocaleDateString("en-GB") + ' '
	            + date.toLocaleTimeString('en-US') + ' - ';
	    } else {
	        initial = date.toLocaleDateString("en-GB") + ' ' + date.toLocaleTimeString('en-US') + ' - ';
	    }
	    var textarea = document.getElementById('id_comments');
	    $("#id_comments_cloned").on('input', function() {
	        $("#id_comments").val(initial + $(this).val());
	        textarea.scrollTop = textarea.scrollHeight;
	    });
	    textarea.scrollTop = textarea.scrollHeight;
	}
	var status, reason, more_details, next_appointment_date, next_appointment_time;
	function initialValues() {
	    status = $('#id_status').val();
	    reason = $('#id_reason').val();
	    more_details = $('#id_more_details').val();
	    next_appointment_date = $('#id_next_appointment_0').val();
	    next_appointment_time =  $('#id_next_appointment_1').val();
	}
	function checkUpdates() {
	    if (window.location.pathname.substring(window.location.pathname.lastIndexOf('/') - 3) == 'add/') {
	        return true;
	    }
	    status_new = $('#id_status').val();
	    reason_new = $('#id_reason').val();
	    more_details_new = $('#id_more_details').val();
	    next_appointment_date_new = $('#id_next_appointment_0').val();
	    next_appointment_time_new =  $('#id_next_appointment_1').val();
	    return status_new != status || reason_new != reason
	        || more_details != more_details_new || next_appointment_date != next_appointment_date_new
	        || next_appointment_time != next_appointment_time_new;
	}
	function check_value_for_select() {
        var selected = $("select#id_channelpartner option:selected").html();
        if (selected != undefined && selected != '') {
            if($("#select2-id_channelpartner-container").html() == "") {
                $("#select2-id_channelpartner-container").html(selected);
            }
        }
    }
    function enable_edit_function() {
        var edit = $("#change_id_channelpartner");
        var customer_pk = $("select#id_channelpartner").val();
        if (edit.length != 0 && customer_pk != undefined && customer_pk != "") {
            var href_val = edit.attr("data-href-template").replace("__fk__", customer_pk);
            edit.attr("href", href_val);
        }
    }
	$(document).ready(function(){
		$("#fieldset-3 .control-label label").addClass("required");
		showHideMoreDetails($("#id_reason").val());
		setTimeout(function() {
			$('ul.timelist').each(function(num, el) {
			time_format = get_format('TIME_INPUT_FORMATS')[0];
			$(el).html('');
			for (i=8; i<20; i++) {
			  var time = new Date(1970,1,1,i,0,0);
			  lnk = "javascript:DateTimeShortcuts.handleClockQuicklink(" + num + ", " + i + ");"
			  $(el).append('<li><a href="' + lnk + '">' + time.strftime(time_format) + '</a></li>');
			}
		});
		}, 1000);
		
		$("#id_reason").on('change', function() {
			showHideMoreDetails($(this).val());
		});
		$("#id_status").on('change', function (){
			$("#select2-id_reason-container > span.select2-selection__clear").mousedown();
		});
		$("ul.errorlist > li").addClass("text-danger");
		mockCommentsSection();
		initialValues();
		$('#lead_form').on('submit', function(e) {
		    if (checkUpdates()) {
		        if ($("#id_comments_cloned").val() == '' && $("div.alert-danger").length == 0) {
		            e.preventDefault();
		            alert("Comment is required field");
		            $("#id_comments_cloned").focus();
		        }
		    }
		});
		$('select#id_channelpartner').bind("DOMSubtreeModified", check_value_for_select);
		$("select#id_channelpartner").on('change', enable_edit_function);
	});
}(this.jQuery));
