var showit = function() {
    jq('#content').fadeOut('fast', 'swing', function() {
        jq('#loading').fadeIn('fast');
    });
}

jQuery("#failure_shower").click(function(){
    jQuery('.failed_rows').toggle();
    jQuery('.successful_rows').toggle();
    jQuery('.FailsLikeABojan').toggle();
    jQuery('.WorksLikeABoss').toggle();
})

jQuery('#redirect_leads').click(function(){
    showit();
    jq.get('list2', function(data){
            swapit(data)
        })
})
