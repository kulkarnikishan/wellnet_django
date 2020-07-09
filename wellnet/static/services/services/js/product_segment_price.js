(function ($) {
	function showHideVehicleCategory() {
		if ($("#id_segment").val() == 5) {
			$("div.field-vehicle_category").show();
		} else {
			$('#id_vehicle_category').prop('selectedIndex',0);
			$("div.field-vehicle_category").hide();
		}
	}
	$(document).ready(function(){
		$("input[name=_addanother]").remove();
		$("input[name=_continue]").remove();
		$("#id_segment").change(function() {
			showHideVehicleCategory();
		});
		showHideVehicleCategory();
	});
}(this.jQuery));
