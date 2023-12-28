/*
 * @Author: czqczqzzzzzz(czq)
 * @Email: tenchenzhengqing@qq.com
 * @Date: 2023-09-03 17:31:26
 * @LastEditors: error: git config user.name & please set dead value or install git
 * @LastEditTime: 2023-12-21 15:12:14
 * @FilePath: \boya_upload_test_file_sys\static\scripts.js
 * @Description: JS逻辑
 *
 * Copyright (c) by czqczqzzzzzz(czq), All Rights Reserved.
 */

let console_outputs = null;
let isUploadRequest = false; // 跟踪是否为上传请求

// 刷新之前保存滚动条
window.addEventListener("beforeunload", function () {
  sessionStorage.setItem("scrollPosition", window.scrollY);
});

/**
 * @description: 当浏览器挂载页面的时候加载逻辑
 * @return {*}
 */

console_outputs = document.getElementById("console_outputs");

let text = sessionStorage.getItem("store");
if (text) {
  let parser = new DOMParser();
  let doc = parser.parseFromString(text, "text/html");
  console_outputs.innerHTML = doc.body.innerHTML;
  sessionStorage.removeItem("store");
}

// 控制滚动条在底端
console_outputs.scrollTop = console_outputs.scrollHeight;

const socket = io.connect("http://" + document.domain + ":" + location.port);

socket.on('connect', function () {
  var currentSid = socket.id;

  fetch(`/get_socketid?sid=${socket.id}`, {
    method: 'POST',
    body: JSON.stringify({ sid: currentSid }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.ok) {
      // 在这里处理成功响应
      console.log('Socket ID sent to server successfully.');
    } else {
      // 处理失败响应
      console.error('Failed to send Socket ID to server.');
    }
  })
  .catch(error => {
    // 处理网络错误
    console.error('Network error:', error);
  });
});

socket.on("console_log", (data) => {
  if (data.trim() === "") {
    return;
  }

  let pre = document.createElement("pre");
  pre.append(document.createTextNode(data));
  console_outputs.appendChild(pre);

  // 当有新的输出时，自动滚动到底部
  console_outputs.scrollTop = console_outputs.scrollHeight;
});

// 刷新后恢复滚动位置
if (sessionStorage.getItem("scrollPosition") !== null) {
  window.scrollTo(0, parseInt(sessionStorage.getItem("scrollPosition")));
}

async function updateSys() {
  document.getElementById('bottomSpan').textContent = "系统正在更新...";
  alert("正在更新系统，请稍等...");
  const maxAttempts = 10;  // 设置最大轮询次数
  let attempts = 0;

  const intervalId = setInterval(async function () {
    try {
      if (attempts >= maxAttempts) {
        clearInterval(intervalId);  // 达到最大轮询次数后清除轮询
        alert("系统更新已超时");
        document.getElementById('bottomSpan').textContent = "系统更新超时";
        return;
      }

      const response = await fetch(`/check_update?sid=${socket.id}`);
      const data = await response.json();

      if (data.status === "update_complete") {
        clearInterval(intervalId);  // 更新完成后清除轮询
        document.getElementById('bottomSpan').textContent = "系统更新完成";
        fetch(`/restartSys?sid=${socket.id}`)
        setTimeout(function () {
          alert("系统已更新完成");
          location.reload();
        }, 0);
      } else if (data.status === "no_update") {
        clearInterval(intervalId);  // 没有更新时清除轮询
        document.getElementById('bottomSpan').textContent = "没有可用更新";
        alert("没有可用更新");
      } else if (data.status === "updating") {
        // 继续轮询
      } else {
        clearInterval(intervalId);  // 处理其他状态
        if (document.getElementById('bottonSpan').textContent == '系统更新完成'){
          alert("系统已更新完成");
          location.reload();
        }else{
        document.getElementById('bottomSpan').textContent = "未知状态";
        alert("未知状态：" + data.status);
        }
      }
    } catch (error) {
      console.error(error);
      clearInterval(intervalId);  // 处理错误情况
      document.getElementById('bottomSpan').textContent = "更新失败";
      alert("更新失败：" + error.message);
    }

    attempts++;
  }, 2000);  // 设置轮询间隔
}


/**
 * @description: 上传文件夹和文件的逻辑
 * @param {*} event 事件对象
 * @return {*}
 */
function uploadFilesAndFolders(event) {
  event.preventDefault(); // 阻止默认事件

  // 选择逻辑
  const files = document.getElementById("files").files;
  const folders = document.getElementById("folder").files;
  if (files.length === 0 && folders.length === 0) {
    alert("您没有选择任何文件或文件夹。");
    return;
  }

  const formData = new FormData(document.querySelector("form"));
  isUploadRequest = true; // 设置上传请求标志

  fetch(`/upload?sid=${socket.id}`, {
    method: "POST",
    headers: {
      //   'Cache-Control': 'no-cache'
      // "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        NProgress.start();
        sessionStorage.setItem("store", console_outputs.innerHTML);
        window.location.reload(true);
        NProgress.done();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const filesInput = document.getElementById("files");
  const filePathDisplay = document.getElementById("filePathDisplay");

  if (filesInput && filePathDisplay) {
    filesInput.addEventListener("change", function () {
      const files = this.files;
      if (files.length > 0) {
        // 显示第一个文件的路径， files 来显示所有选择的文件的路径
        filePathDisplay.textContent = files[0].name;
      } else {
        filePathDisplay.textContent = "";
      }
    });
  }
});

/**
 * @description: 使用文件绝对路径上传文件
 * @param {Object} event 事件对象
 * @return {*}
 */
function uploadUsingPath(event) {
  // 阻止表单的默认行为
  event.preventDefault();

  const manualFilePath = document.getElementById("manualFilePath").value;
  const scriptSelection = document.getElementById(
    "scriptSelectorForPath"
  ).value;

  if (!manualFilePath) {
    alert("请提供文件路径");
    return; // 直接返回
  }

  // 构建请求体
  const requestBody = new URLSearchParams();
  requestBody.append("manualFilePath", manualFilePath);
  requestBody.append("scriptSelectorForPath", scriptSelection);

  isUploadRequest = true; // 设置上传请求标志
  // 直接发送请求到服务器
  fetch(`/upload_by_path?sid=${socket.id}`, {
    method: "POST",
    // headers: {
    //   "Content-Type": "application/x-www-form-urlencoded",
    // },
    body: requestBody,
  })
    .then((response) => {
      if (response.ok) {
        NProgress.start();
        sessionStorage.setItem("store", console_outputs.innerHTML);
        window.location.reload(true);
        NProgress.done();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function deleteButtonOnClickForFile(button) {
  const fileInputs = document.getElementById("fileInputs");
  const newInputWrapper = document.createElement("div");
  newInputWrapper.classList.add("inputWrapper");

  const newInput = document.createElement("input");
  const fileInput = document.getElementById("files");
  // 遍历源输入框的所有属性
  for (let i = 0; i < fileInput.attributes.length; i++) {
    const attr = fileInput.attributes[i];
    newInput.setAttribute(attr.name, attr.value);
  }

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "删除选择项";
  const deleteChooseForFile = document.getElementById("deleteChooseForFile");
  for (let i = 0; i < deleteChooseForFile.attributes.length; i++) {
    const attr = deleteChooseForFile.attributes[i];
    deleteButton.setAttribute(attr.name, attr.value);
  }

  fileInputs.removeChild(button.parentNode);

  if (fileInputs.childElementCount < 1) {
    // 检查是否只剩下一个输入框
    newInputWrapper.appendChild(newInput);
    newInputWrapper.appendChild(deleteButton);
    fileInputs.appendChild(newInputWrapper);
  }
}

function addInputForFile() {
  const fileInputs = document.getElementById("fileInputs");
  const newInputWrapper = document.createElement("div");
  newInputWrapper.classList.add("inputWrapper");

  const newInput = document.createElement("input");
  const fileInput = document.getElementById("files");
  // 遍历源输入框的所有属性
  for (let i = 0; i < fileInput.attributes.length; i++) {
    const attr = fileInput.attributes[i];
    newInput.setAttribute(attr.name, attr.value);
  }

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "删除选择项";
  const deleteChooseForFile = document.getElementById("deleteChooseForFile");
  for (let i = 0; i < deleteChooseForFile.attributes.length; i++) {
    const attr = deleteChooseForFile.attributes[i];
    deleteButton.setAttribute(attr.name, attr.value);
  }

  newInputWrapper.appendChild(newInput);
  newInputWrapper.appendChild(deleteButton);
  fileInputs.appendChild(newInputWrapper);
}

function deleteButtonOnClickForFolder(button) {
  const folderInputs = document.getElementById("folderInputs");
  const newInputWrapper = document.createElement("div");
  newInputWrapper.classList.add("inputWrapper");

  const newInput = document.createElement("input");
  const folderInput = document.getElementById("folder");
  // 遍历源输入框的所有属性
  for (let i = 0; i < folderInput.attributes.length; i++) {
    const attr = folderInput.attributes[i];
    newInput.setAttribute(attr.name, attr.value);
  }

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "删除选择项";
  const deleteChooseForFolder = document.getElementById(
    "deleteChooseForFolder"
  );
  for (let i = 0; i < deleteChooseForFolder.attributes.length; i++) {
    const attr = deleteChooseForFolder.attributes[i];
    deleteButton.setAttribute(attr.name, attr.value);
  }

  folderInputs.removeChild(button.parentNode);

  if (folderInputs.childElementCount < 1) {
    // 检查是否只剩下一个输入框
    newInputWrapper.appendChild(newInput);
    newInputWrapper.appendChild(deleteButton);
    folderInputs.appendChild(newInputWrapper);
  }
}

function addInputForFolder() {
  const folderInputs = document.getElementById("folderInputs");
  const newInputWrapper = document.createElement("div");
  newInputWrapper.classList.add("inputWrapper");

  const newInput = document.createElement("input");
  const folderInput = document.getElementById("folder");
  // 遍历源输入框的所有属性
  for (let i = 0; i < folderInput.attributes.length; i++) {
    const attr = folderInput.attributes[i];
    newInput.setAttribute(attr.name, attr.value);
  }

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "删除选择项";
  const deleteChooseForFolder = document.getElementById(
    "deleteChooseForFolder"
  );
  for (let i = 0; i < deleteChooseForFolder.attributes.length; i++) {
    const attr = deleteChooseForFolder.attributes[i];
    deleteButton.setAttribute(attr.name, attr.value);
  }

  newInputWrapper.appendChild(newInput);
  newInputWrapper.appendChild(deleteButton);
  folderInputs.appendChild(newInputWrapper);
}

// let selectedFiles = [];

// function clearInput(inputId) {
//   const input = document.getElementById(inputId);
//   input.value = "";

//   if (inputId === "files") {
//     selectedFiles = selectedFiles.filter((file) => !file.webkitRelativePath);
//     document.getElementById(
//       "files"
//     ).labels[0].textContent = `选择单个或多个文件：`;
//   } else {
//     selectedFiles = selectedFiles.filter((file) => file.webkitRelativePath);
//     document.getElementById(
//       "folder"
//     ).labels[0].textContent = `选择整个文件夹中的所有文件：`;
//   }

//   return false; // 防止表单提交和页面刷新
// }

// function updateFileCount() {
//   const fileCount = selectedFiles.filter(
//     (file) => !file.webkitRelativePath
//   ).length;
//   const folderCount = selectedFiles.filter(
//     (file) => file.webkitRelativePath
//   ).length;

//   document.getElementById(
//     "files"
//   ).labels[0].textContent = `已选择 ${fileCount} 个文件`;
//   document.getElementById(
//     "folder"
//   ).labels[0].textContent = `已选择 ${folderCount} 个文件`;
// }

// document.getElementById("files").addEventListener("change", function (e) {
//   selectedFiles = Array.from(e.target.files);
//   updateFileCount();
// });

// document.getElementById("folder").addEventListener("change", function (e) {
//   selectedFiles = Array.from(e.target.files);
//   updateFileCount();
// });

// var selectedFiles = []
// document.getElementById('files').addEventListener('change', (e) => {
//   const files = e.target.files;
//   for (let i = 0; i < files.length; i++) {
//     selectedFiles.push(files[i]);
// console.log(selectedFiles);

// }
// })

// 清除下载日志里的文件
// 为XP兼容
document.addEventListener("DOMContentLoaded", function () {
  var clearFilesBtn = document.getElementById("clearFilesBtn");
  if (clearFilesBtn) {
    clearFilesBtn.addEventListener("click", function () {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/clear_files", true);
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
          var data = JSON.parse(xhr.responseText);
          if (data.success) {
            NProgress.start();
            window.location.href = window.location.origin; // 导航到应用的根URL
            NProgress.done();
          } else {
            alert("清除文件失败!");
          }
        }
      };
      xhr.send();
    });
  }
  const goToHomePageButton = document.getElementById("go-to-home-page");
  if (goToHomePageButton) {
    goToHomePageButton.addEventListener("click", function () {
      // 这里 data.redirect 已经被定义并包含了要跳转的 index 页面的 URL
      NProgress.start();
      window.location.href = window.location.origin;
      NProgress.done();
    });
  }
});

// 回到页面顶部的逻辑
document.addEventListener("DOMContentLoaded", function () {
  const backToTopButton = document.getElementById("back-to-top");
  let buttonVisible = false;

  // 根据滚动位置显示或隐藏“返回页首”按钮
  window.addEventListener("scroll", function () {
    if (window.scrollY > 300 && !buttonVisible) {
      backToTopButton.style.display = "block";
      backToTopButton.classList.add("button-bounce-in");
      buttonVisible = true;
    } else if (window.scrollY <= 300 && buttonVisible) {
      backToTopButton.classList.remove("button-bounce-in");
      backToTopButton.classList.add("button-bounce-out");
      setTimeout(function () {
        backToTopButton.style.display = "none";
        backToTopButton.classList.remove("button-bounce-out");
      }, 600);
      buttonVisible = false;
    }
  });

  // 平滑滚动到顶部并在单击时添加反弹动画
  backToTopButton.addEventListener("click", function () {
    // 添加动画
    backToTopButton.classList.add("button-bounce");

    // 平滑滚动到顶部
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

    // 动画完成后移除
    setTimeout(function () {
      backToTopButton.classList.remove("button-bounce");
    }, 600);
  });
});

// 去往页面底部的逻辑
document.addEventListener("DOMContentLoaded", function () {
  const scrollToBottomButton = document.getElementById("go-to-bottom");
  let buttonVisible = false;
  // 页面刚加载应该就有一次
  scrollToBottomButton.style.display = "block";
  scrollToBottomButton.classList.add("button-bounce-in");
  // 根据滚动位置显示或隐藏“滚动到底”按钮
  window.addEventListener("scroll", function () {
    if (
      window.scrollY + window.innerHeight < document.body.scrollHeight - 300 &&
      !buttonVisible
    ) {
      scrollToBottomButton.style.display = "block";
      scrollToBottomButton.classList.add("button-bounce-in");
      buttonVisible = true;
    } else if (
      window.scrollY + window.innerHeight >= document.body.scrollHeight - 300 &&
      buttonVisible
    ) {
      scrollToBottomButton.classList.remove("button-bounce-in");
      scrollToBottomButton.classList.add("button-bounce-out");
      setTimeout(function () {
        scrollToBottomButton.style.display = "none";
        scrollToBottomButton.classList.remove("button-bounce-out");
      }, 600);
      buttonVisible = false;
    }
  });

  // 单击时平滑滚动到底部
  scrollToBottomButton.addEventListener("click", function () {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  });
});

// 截取下载路径到页面显示文件名
document.addEventListener("DOMContentLoaded", function () {
  const downloadLinks = document.querySelectorAll(
    ".back_style a[data-filename]"
  );

  downloadLinks.forEach((link) => {
    const fullPath = link.getAttribute("data-filename");
    const fileName = fullPath.split("\\").pop(); // 获取路径的最后一部分作为文件名
    link.textContent = fileName; // 设置链接的文本内容为文件名
  });
});

// 侧边栏行为
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const rightSidebar = document.getElementById("right-sidebar"); // 获取右侧侧边栏元素

  // 当鼠标移动到窗口的左边缘时显示侧边栏
  document.addEventListener("mousemove", function (event) {
    let x = event.clientX; // 获取鼠标的X坐标
    let windowWidth = window.innerWidth; // 获取窗口的宽度

    if (event.clientX < 20) {
      sidebar.style.left = "0";
    }

    // 当鼠标移动到窗口的右边缘时显示右侧侧边栏
    if (x >= windowWidth - 20) {
      // 20是一个阈值，与左侧侧边栏相同
      rightSidebar.style.right = "0"; // 显示 right-sidebar
    }
  });

  // 当鼠标移出左侧侧边栏时隐藏侧边栏
  sidebar.addEventListener("mouseleave", function () {
    sidebar.style.left = "-250px";
  });

  // 当鼠标移出右侧侧边栏时隐藏侧边栏
  rightSidebar.addEventListener("mouseleave", function () {
    let sidebarWidth = rightSidebar.offsetWidth;
    rightSidebar.style.right = -sidebarWidth + "px";
  });

  // 找到所有有子菜单的菜单项
  const hasSubmenuItems = document.querySelectorAll(".has-submenu");

  // 为每一个添加点击事件监听器
  hasSubmenuItems.forEach(function (item) {
    item.addEventListener("click", function (event) {
      const submenu = item.querySelector(".submenu");
      if (submenu.style.maxHeight) {
        submenu.style.maxHeight = null;
      } else {
        submenu.style.maxHeight = submenu.scrollHeight + "px";
      }
    });
  });

  const folderItems = document.querySelectorAll(".folder");

  folderItems.forEach(function (folder) {
    folder.addEventListener("click", function (event) {
      const nextLi = folder.nextElementSibling; // 获取紧接在 folder 后面的 li 元素
      if (nextLi) {
        const ul = nextLi.querySelector("ul"); // 在 nextLi 内部找到 ul

        if (ul) {
          // 确保 ul 不是 null
          if (ul.style.display === "none" || !ul.style.display) {
            ul.style.display = "block";
            folder.querySelector(".triangle").style.transform = "rotate(0deg)";
          } else {
            ul.style.display = "none";
            folder.querySelector(".triangle").style.transform =
              "rotate(270deg)";
          }
        }
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const rightSidebar = document.getElementById("right-sidebar");

  // 当鼠标移动到窗口的右边缘时显示右侧侧边栏
  document.addEventListener("mousemove", function (event) {
    let x = event.clientX;
    let windowWidth = window.innerWidth;

    if (x >= windowWidth - 20) {
      rightSidebar.classList.remove("closed");
    }
  });

  // 当鼠标离开右侧侧边栏时隐藏
  rightSidebar.addEventListener("mouseleave", function () {
    rightSidebar.classList.add("closed");
  });
});

//点击的对话框逻辑

// 获取按钮元素、覆盖和对话框
const open = document.getElementById("openDialog");
const overlay = document.getElementById("overlay");
const dialog = document.getElementById("uploadDialog");

// 将事件侦听器添加到按钮以打开对话框
open.addEventListener("click", openDialog);

// 当打开对话框时调用填充函数
function openDialog() {
  overlay.style.display = "block";
  dialog.style.display = "block"; // 重新设置display为block
  dialog.style.visibility = "visible";
  setTimeout(() => {
    dialog.style.opacity = "1";
    overlay.style.opacity = "1";
  }, 50);

  // 在这里初始化 tempScripts
  tempScripts = Array.from(
    document.getElementById("scriptSelectorForChoose").options
  ).map((opt) => opt.value);
  populateScriptList(); // 填充脚本列表
}
// 关闭对话框
function closeDialog(id) {
  overlay.style.opacity = "0";
  id.style.opacity = "0";
  setTimeout(() => {
    overlay.style.display = "none";
    id.style.display = "none"; // 在动画完成后隐藏对话框
  }, 500); // 500ms 是 opacity 的 transition 时间
}

const aboutDialog = document.getElementById('aboutDialog')
function showUpdateLog(){
  overlay.style.display = "block";
  aboutDialog.style.display = "block"; // 重新设置display为block
  aboutDialog.style.visibility = "visible";
  setTimeout(() => {
    aboutDialog.style.opacity = "1";
    overlay.style.opacity = "1";
    loadTxtContent();
  }, 50);

  
}

let tempScripts = [];
let deletedScripts = [];

// 函数，用于填充脚本列表
function populateScriptList() {
  const scriptListDiv = document.getElementById("scriptList");
  scriptListDiv.innerHTML = ""; // 清除任何现有内容

  tempScripts.forEach((script) => {
    const scriptItem = document.createElement("div");
    scriptItem.className = "script-item";

    const scriptName = document.createElement("span");

    scriptName.innerText = script;

    const deleteBtn = document.createElement("button");
    deleteBtn.innerText = "移除脚本";
    deleteBtn.onclick = function () {
      // 从临时列表中移除脚本
      const index = tempScripts.indexOf(script);
      if (index > -1) {
        tempScripts.splice(index, 1);
      }
      deletedScripts.push(script);
      // 重新填充列表
      populateScriptList();
    };


    scriptItem.appendChild(scriptName);
    scriptItem.appendChild(deleteBtn);
    scriptListDiv.appendChild(scriptItem);

  });
}

marked.setOptions({
  gfm: true,  // 启用 GitHub 风格的 Markdown。
  tables: true  // 启用 GFM 表格。需要 gfm 为 true。
});

function displayMarkdownContent(data) {
  const informationDiv = document.getElementById('information');
  const htmlContent = marked.parse(data);
  informationDiv.innerHTML = htmlContent;
}


// 留着备用，手动匹配格式
// function parseMarkdown(text) {
//   const lines = text.split('\n');
//   const parsedLines = lines.map(line => {
//       if (line.startsWith('###')) return `<h3>${line.slice(3).trim()}</h3>`;
//       if (line.startsWith('##')) return `<h2>${line.slice(2).trim()}</h2>`;
//       if (line.startsWith('#')) return `<h1>${line.slice(1).trim()}</h1>`;
//       return line;
//   });
//   return parsedLines.join('\n');
// }

// 这个函数会从项目的根目录加载 a.txt 文件并将其内容显示在 <div id="information"></div> 中
function loadTxtContent() {
  const informationDiv = document.getElementById('information');

  fetch(`/aboutInfo?sid=${socket.id}`)
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      return response.text();  // 返回响应的文本内容
  })
  .then(data => {
    displayMarkdownContent(data);
    // informationDiv.innerHTML  = parseMarkdown(data);
  })
  .catch(error => {
      console.error('Error fetching the .txt file:', error);
  });
}



function checkDuplicateNames(uploadedFiles) {
  // 1. 获取所有已存在的script名称
  let existingScripts = tempScripts

  // 2. 检查待上传的文件名是否在这些名称中
  for (let file of uploadedFiles) {
      if (existingScripts.includes(file.name)) {
          // 3. 如果有重名，显示警告对话框
          if(confirm("文件名 " + file.name + " 已存在，确定覆盖此文件吗？")){
            return true
          }else{
          return false
          }
      }
  }
  return true;
}

function submitChanges() {

  let formData = new FormData();
    let jsonString = JSON.stringify(deletedScripts);
    formData.append("delete_files", jsonString);

    let uploadedFiles = document.getElementById("newScripts").files;
  
  if(!checkDuplicateNames(uploadedFiles)){
    
    return;
  }
  if (confirm("确定要保存更改吗？")) {
    
    for (let file of uploadedFiles) {
      formData.append("upload_files", file);
    }

    fetch(`/manage_scripts?sid=${socket.id}`, {
      method: "POST",
      body: formData,
    }).then((response) => {
      if (response.ok) {
        // 刷新页面以反映更改
        closeDialog(dialog);
        sessionStorage.setItem("store", console_outputs.innerHTML);
        setTimeout(() => {
          window.location.reload(true);
        }, 3000);
      }
    });
  }
}



document.getElementById('showInstruction').addEventListener('click', function() {
  openPdfDialog();
});

function openPdfDialog() {
  const overlay = document.getElementById('overlay');
  const pdfDialog = document.getElementById('pdfDialog');
  overlay.style.display = 'block';
  pdfDialog.style.display = 'block';
  setTimeout(() => {
      overlay.style.opacity = '1';
      pdfDialog.style.opacity = '1';
      pdfDialog.style.visibility = 'visible';
      // 在过渡效果完成后设置 PDF 的 src 属性
      setTimeout(() => {
          const pdfContainer = document.getElementById('pdfContainer');
          pdfContainer.src = '/static/README.pdf'; // 替换为您的 PDF 文件路径
      }, 500); // 与 CSS 中的过渡效果时间相匹配
  }, 50);
}

function closePdfDialog() {
  const overlay = document.getElementById('overlay');
  const pdfDialog = document.getElementById('pdfDialog');
  const pdfContainer = document.getElementById('pdfContainer');
  overlay.style.opacity = '0';
  pdfDialog.style.opacity = '0';
  // 在开始过渡效果时清除 PDF 的 src 属性，防止在关闭对话框时显示模糊的 PDF
  pdfContainer.src = '';
  setTimeout(() => {
      overlay.style.display = 'none';
      pdfDialog.style.display = 'none';
      pdfDialog.style.visibility = 'hidden';
  }, 500); // 500ms 是 opacity 的 transition 时间
}
