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
var human_to_epoch = function(input_date) {
    var split_date = input_date.split('/');
    var d = new Date(split_date[2], split_date[0]-1, split_date[1], 0,0,0,0);
    var close_time = d.getTime();
    return close_time.toString();
}
jq(function(){
    var confirmation ='You have selected leads on this page.\nAre you sure you want to leave them in their current state?'
    jq('input#datepicker').datepicker();
    jq.datepicker.setDefaults(jq.datepicker.regional['']);
    
    jq('.close_button').click(function(){
        if (!jq('#datepicker')[0].value) {
            alert('Please select a date.');
            return false;
        } else if (!jq(':checked').length) {
            alert('No leads are selected!');
            return false;
        };
        var raw_date = jq('#datepicker').val();
        var close_time = human_to_epoch(raw_date);
        var search_term = jq('#passed_term').val() || '';
        var post_data = jq('.lead_box:checked').serialize() + "&offset=" + jq('#offset').val() + "&close_time=" + close_time + "&search=" + search_term;
        showit();
        jq.post("close", post_data, function(data) { swapit(data) });
    })
    jq('.prev').click(function() {
        if (jq(':checked').length) {
            confirm(confirmation);
        }
        showit();
        var post_data = {
            offset: jq('#offset').val(),
            prev: 'prev'
        }
        jq.post("list", post_data, function(data) { swapit(data) });
    })
    jq('.next').click(function() {
        if (jq(':checked').length) {
            confirm(confirmation)
        }
        showit();
        var post_data = {
            offset: jq('#offset').val(),
            next: 'next'
        }
        jq.post("list", post_data, function(data) { swapit(data) });
    })
    jq('#select_all').click(function(){
        jq('.lead_box').each(function(){
            jq(this).attr('checked', !jq(this)[0].checked);
        })
    })
    jq('#search_butto').click(function(){
        var post_data = { search_term: jq('.search_leads').val() };
        showit();
        jq.post('search', post_data, function(data){ swapit(data) });
    })
    jq('#csv_redirect').click(function(){
	showit();
        jq.get('csv', function(data){
            swapit(data)
        })
    })
});

