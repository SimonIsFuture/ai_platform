// var vm = new Vue({
//     delimiters: ['{[', ']}'],
//     data: []
// })


// 根据视频播放时间来控制滚动条
function draw_canvas() {
    axios.get('/video/get_bar', { params: { 'actor_id': $('#data_container').attr('actor_id'), 'play_id': $('#data_container').attr('play_id') } })
        .then(function (response) {
            console.log(response);
            json_data = response.data.process_bar
            var canvas = document.getElementById("process_bar");
            var context = canvas.getContext("2d");
            var width = 500 * 5.45;
            var width = 500;
            context.fillStyle = "blue";
            for (var i = 0; i < json_data.length; i++) {
                var mid = width * json_data[i]
                context.fillRect(mid, 0, 5, 25)
            }
        })
        .catch(function (error) {
            console.log(error);
        });
}

function change_subtitle(){
    axios.get('/video/get_subtitle_data', { params: { 'play_id': $('#data_container').attr('play_id') } })
        .then(function (response) {
            subtitle = response.data.data;
             
            setInterval(function () {
                var cur_time = document.getElementById("my_video").currentTime;
                //console.log(subtitle)
                for(var i=0; i < subtitle.length; i++){
                    d = subtitle[i]
                    var start_time = d.start
                    var end_time = d.end       
                         
                    if( cur_time >= start_time && cur_time <= end_time){
                        $('#subtitle').text(d.text)
                    }
                }
            }, 500);
        })
        .catch(function (error) {
            console.log(error);
        });
}

draw_canvas()
//interval_face_detection()
change_subtitle()
