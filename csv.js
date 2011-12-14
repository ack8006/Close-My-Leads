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
jq(function(){
  jq('#csv_submit').click(function(){
    if (!jq('#csv').val()) {
        alert("you didn't enter your csv!");
        return false;
    } else {
        var post_data = {
            csv: jq('#csv').val()
        }
        showit();
        jq.post("csv", post_data, function(data) { swapit(data)});
    }
  })
})
