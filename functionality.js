$( document ).ready(function() {
    $('#calculate').click(function() {
        doSend('compute::' + $('#startInput').val() + '::' + $('#endInput').val());
        $('#calculate').attr("disabled", "disabled");
        $('#startInput').attr("disabled", "disabled");
        $('#endInput').attr("disabled", "disabled");
    });
});