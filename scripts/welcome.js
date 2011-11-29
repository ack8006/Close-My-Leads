var jq;
window.jq = jQuery.noConflict(true);
function clearCookie(name, domain, path){
    var domain = domain || document.domain;
    var path = path || "/";
    document.cookie = name + "=; expires=" + new Date + "; domain=" + domain + "; path=" + path; return document.cookie
};
clearCookie('close-my-leads.auth', '.app.hubspot.com', location.pathname.split('/').slice(0, 5).join('/'));
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
            api_key: jq('#api_key').val()
        }
        jq.post("home", post_data, function(data) { swapit(data) });
    })
})

