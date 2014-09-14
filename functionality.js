$( document ).ready(function() {
    $('#startInput').on('input', function() {
        tags = [];
        $('#startInput').autocomplete({
            source: tags
        });
    });
    
    $('#endInput').on('input', function() {
        tags = [];
        $('#endInput').autocomplete({
            source: tags
        });
    });
    
    $('#calculate').click(function() {
        doSend('compute::' + $('#startInput').val() + '::' + $('#endInput').val());
    });
});