//创建服务
var create_service = (db_name, entity_id) => {
  data = {
    Action: "CreateService",
    DbName: db_name,
    AppKey: "test@qq.com",
    EntityId: entity_id,
    URL: "http://182.42.255.14:8502/ai",
  };
  axios
    .post("/obs", data)
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });
};
//创建FaceDb
var createDb = (app_key, database) => {
  axios
    .post("/obs", {
      Action: "CreateFaceDb",
      AppKey: app_key,
      Name: database,
      URL: "http://182.42.255.14:8502/ai",
    })
    .then(function (response) {
      console.log(response);
      createTestFaceEntity();
    })
    .catch(function (error) {
      console.log(error);
    });
};

// 页面加载完成，初始化程序
var date = new Date();
let cur_time = date.getTime(); //获取当前日期

//初始化各项参数
let app_key = "test@qq.com";
let database = "default";
let confirmed = false;
let entity_id = cur_time;

$(document).ready(() => {
  //创建服务
  create_service(database, entity_id);
  //初始化CupLoad
  var cupload = new Cupload({
    ele: "#cupload",
    num: 5,
    url: "/file_upload",
  });
  //创建db
  createDb(app_key, database)
});

//$("#user_info").hide();

//检查是否是合法的邮箱地址
var testMail = (addr) => {
  var emreg = /^\w{3,}(\.\w+)*@[A-z0-9]+(\.[A-z]{2,5}){1,2}$/;
  return emreg.test(addr);
};

$("#confirm").click(() => {
  app_key = $("#app_key").val();
  if (!testMail(app_key)) {
    alert("不正确的邮箱地址，请检查!");
    return;
  }
  //获取database
  var t_db = $("#db_name").val();
  if (t_db.length != 0) {
    database = t_db;
  }

  content = "你的app_Key为:" + app_key + " 数据库为:" + database;

  confirmed = true;
  $("#user_info").text(content);
  $("#user_info").show();

  createDb();
});

var canvasImg = (data) => {
  const img = new Image();
  data = data.replace(/\_/g, "/");
  data = data.replace(/\-/g, "+");
  img.src = "data:image/jpeg;base64," + data;
  //生成canvas
  const canvas = document.getElementById("res_canvas");
  canvas.height = 148;
  canvas.width = 148;
  width = canvas.width / img.width;
  height = canvas.height / img.height ;
  const ctx = canvas.getContext("2d");
  //ctx.drawImage(bgImg, 0, 0, 260, 900);
  ctx.drawImage(img,0,0,  canvas.height * height * 2 , canvas.width * width * 2);
};

var createTestFaceEntity = () => {
  data = {
    Action: "AddFaceEntity",
    DbName: database,
    AppKey: app_key,
    EntityId: entity_id,
    URL: "http://182.42.255.14:8502/ai",
  };
  axios
    .post("/obs", data)
    .then(function (response) {
      console.log(response);
    })
    .catch(function (error) {
      console.log(error);
    });
};

var show_faces = (face_ids) => {
  face_ids.forEach((item, index, arr) => {
    console.log(item);
    console.log(item.FaceId);
    data = {
      Action: "GetBase64Data",
      DbName: database,
      FaceId: item.FaceId,
      AppKey: app_key,
      URL: "http://182.42.255.14:8502/ai",
    };
    axios
      .post("obs", data)
      .then(function (response) {
        console.log(response.data);
        image_data = response.data.ImageData;
        canvasImg(image_data);
      })
      .catch(function (error) {
        console.log(error);
      });
  });
};

var get_faces = (face_data) => {
  data = {
    Action: "SearchFace",
    DbName: "default",
    ImageData: face_data,
    Limit: 1,
    AppKey: app_key,
    URL: "http://182.42.255.14:8502/ai",
  };
  axios
    .post("obs", data)
    .then(function (response) {
      console.log(response);
      data = response.data.Data.MatchList[0].FaceItems;
      console.log(data);
      show_faces(data);
    })

    .catch(function (error) {
      console.log(error);
    });
};
