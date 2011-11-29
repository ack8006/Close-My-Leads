var showit = function() {
    jq('#content').fadeOut('fast', 'swing', function() {
        jq('#loading').fadeIn('fast');
    });
}
var swapit = function(data) {
    jq('#content').html(data);
    jq('#loading').fadeOut('fast', 'swing', function() {
        jq('#content').fadeIn('fast');
    });
}

jq(function() {
    jq('#submit').click(function() {
        if (!jq('#api_key').val()) {
            jq('.validate.key').show();
            return false;
        }
        if (jq('#api_key').val()) {
            jq('.validate.key').hide();
        }
        showit();
    var post_data = {
            portalId: jq('#portalId').val(),
            api_key: jq('#api_key').val()
        }
        jq.post("home", post_data, function(data) { swapit(data) });
    })
})

