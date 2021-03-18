const api_url =
  "https://api.github.com/repos/vigneshshettyin/Bulk-Mailer/commits";

// Defining async function
async function getapi(url) {
  // Storing response
  const response = await fetch(url);

  // Storing data in form of JSON
  var data = await response.json();
  console.log(data);
//   mentor section
  document.getElementById("mentor-name1").innerHTML =
    data[0].commit.author.name;
  document.getElementById("mentor-name2").innerHTML =
    data[1].commit.author.name;
  document.getElementById("mentor-name3").innerHTML =
    data[5].commit.author.name;
  document.getElementById("mentor-name4").innerHTML =
    data[3].commit.author.name;
  document.getElementById("img1").src = data[0].author.avatar_url;
  document.getElementById("img2").src = data[1].author.avatar_url;
  document.getElementById("img3").src = data[5].author.avatar_url;
  document.getElementById("img4").src = data[3].author.avatar_url;

  //   contributor section 

  document.getElementById("contributor-name1").innerHTML =
    data[10].commit.author.name;
  document.getElementById("contributor-name2").innerHTML =
    data[11].commit.author.name;
  document.getElementById("contributor-name3").innerHTML =
    data[12].commit.author.name; 
  document.getElementById("contributor-name4").innerHTML =
    data[13].commit.author.name;
  document.getElementById("contributor-name5").innerHTML =
    data[14].commit.author.name;
  document.getElementById("contributor-name6").innerHTML =
    data[15].commit.author.name;   
  document.getElementById("contributor-name7").innerHTML =
    data[16].commit.author.name;
  document.getElementById("contributor-name8").innerHTML =
    data[17].commit.author.name;
  document.getElementById("contributor-name9").innerHTML =
    data[18].commit.author.name;
  document.getElementById("contributor-name10").innerHTML =
    data[19].commit.author.name;
  document.getElementById("contributor-name11").innerHTML =
    data[20].commit.author.name;
  document.getElementById("contributor-name12").innerHTML =
    data[21].commit.author.name;
  document.getElementById("c_img1").src = data[10].author.avatar_url;
  document.getElementById("c_img2").src = data[11].author.avatar_url;
  document.getElementById("c_img3").src = data[12].author.avatar_url;
  document.getElementById("c_img4").src = data[13].author.avatar_url;
  document.getElementById("c_img5").src = data[14].author.avatar_url;
  document.getElementById("c_img6").src = data[15].author.avatar_url;
  document.getElementById("c_img7").src = data[16].author.avatar_url;
  document.getElementById("c_img8").src = data[17].author.avatar_url;
  document.getElementById("c_img9").src = data[18].author.avatar_url;
  document.getElementById("c_img10").src = data[19].author.avatar_url;
  document.getElementById("c_img11").src = data[20].author.avatar_url;
  document.getElementById("c_img12").src = data[21].author.avatar_url;


}
// Calling that async function
getapi(api_url);
