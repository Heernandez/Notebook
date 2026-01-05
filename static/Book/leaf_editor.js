/* global fetch */
(async function () {
  var surface = document.querySelector("[data-editor-surface]");
  var form = document.querySelector("[data-editor-form]");
  var input = document.getElementById("id_content_json");
  var imageButton = document.querySelector("[data-image-button]");
  var imageInput = document.querySelector("[data-image-input]");
  var canvas = document.querySelector("[data-editor-canvas]");
  var imageRemove = document.querySelector("[data-image-remove]");
  if (!surface || !form || !input) return;

  function fallbackDoc(text) {
    if (!text) {
      return { type: "doc", content: [{ type: "paragraph" }] };
    }
    return {
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [{ type: "text", text: text }],
        },
      ],
    };
  }

  var editor = null;
  var uploadUrl = form.getAttribute("data-upload-url");

  function getCookie(name) {
    var value = document.cookie.split("; ").find(function (row) {
      return row.startsWith(name + "=");
    });
    return value ? decodeURIComponent(value.split("=")[1]) : "";
  }

  function uploadImage(file) {
    if (!uploadUrl) return Promise.reject(new Error("Missing upload URL"));
    var data = new FormData();
    data.append("image", file);
    return fetch(uploadUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: data,
    }).then(function (response) {
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      return response.json();
    });
  }

  try {
    var modules = await Promise.all([
      import("https://esm.sh/@tiptap/core@2.6.6"),
      import("https://esm.sh/@tiptap/starter-kit@2.6.6"),
      import("./image_resize.js"),
      import("https://esm.sh/@tiptap/extension-text-style@2.6.6"),
      import("https://esm.sh/@tiptap/extension-color@2.6.6"),
    ]);
    var Editor = modules[0].Editor;
    var StarterKit = modules[1].StarterKit || modules[1].default;
    var ImageResize = modules[2].default || modules[2];
    var TextStyle = modules[3].TextStyle || modules[3].default;
    var Color = modules[4].Color || modules[4].default;
    var initialContent = fallbackDoc("");
    if (input.value) {
      try {
        initialContent = JSON.parse(input.value);
      } catch (error) {
        initialContent = fallbackDoc("");
      }
    }
    editor = new Editor({
      element: surface,
      extensions: [
        StarterKit,
        TextStyle,
        Color,
        ImageResize.configure({ inline: true }),
      ],
      content: initialContent,
      onUpdate: function (payload) {
        input.value = JSON.stringify(payload.editor.getJSON());
      },
    });
  } catch (error) {
    surface.setAttribute("contenteditable", "true");
    surface.classList.add("editor-surface--fallback");
    surface.addEventListener("input", function () {
      input.value = JSON.stringify(fallbackDoc(surface.innerText.trim()));
    });
  }

  function insertImage(url) {
    if (editor) {
      editor.chain().focus().setImage({ src: url, width: 85 }).run();
      return;
    }
    if (document.activeElement === surface) {
      document.execCommand("insertText", false, url);
    } else {
      surface.textContent += url;
    }
  }

  if (imageButton && imageInput) {
    imageButton.addEventListener("click", function () {
      imageInput.click();
    });
    imageInput.addEventListener("change", function () {
      var file = imageInput.files && imageInput.files[0];
      if (!file) return;
      uploadImage(file)
        .then(function (payload) {
          if (payload && payload.url) {
            insertImage(payload.url);
          }
        })
        .catch(function () {
          insertImage("[image upload failed]");
        });
      imageInput.value = "";
    });
  }

  document.querySelectorAll("[data-heading]").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!editor) return;
      var value = button.getAttribute("data-heading");
      if (value === "paragraph") {
        editor.chain().focus().setParagraph().run();
        return;
      }
      var level = parseInt(value, 10);
      editor.chain().focus().toggleHeading({ level: level }).run();
    });
  });

  var lastSelection = null;
  if (editor) {
    editor.on("selectionUpdate", function () {
      lastSelection = editor.state.selection;
    });
  }

  var activeColor = null;
  var colorInput = document.querySelector("[data-color-input]");
  if (colorInput) {
    colorInput.addEventListener("input", function () {
      if (!editor) return;
      activeColor = colorInput.value;
      if (lastSelection) {
        editor.view.dispatch(editor.state.tr.setSelection(lastSelection));
      }
      editor.chain().focus().setColor(activeColor).run();
    });
  }

  if (editor) {
    editor.on("selectionUpdate", function () {
      var currentColor = editor.getAttributes("textStyle").color || null;
      if (currentColor) {
        activeColor = currentColor;
        if (colorInput) {
          colorInput.value = currentColor;
        }
      }
    });

    editor.on("transaction", function () {
      if (!activeColor) return;
      if (editor.isActive("textStyle", { color: activeColor })) return;
      editor.chain().focus().setColor(activeColor).run();
    });
  }

  function positionRemoveButton() {
    if (!editor || !canvas || !imageRemove) return;
    if (!editor.isActive("image")) {
      imageRemove.classList.remove("is-visible");
      return;
    }
    var from = editor.state.selection.from;
    var dom = editor.view.nodeDOM(from);
    var img = null;
    if (dom && dom.nodeType === 1 && dom.tagName === "IMG") {
      img = dom;
    } else if (dom && dom.nodeType === 3 && dom.parentNode && dom.parentNode.tagName === "IMG") {
      img = dom.parentNode;
    } else if (dom && dom.querySelector) {
      img = dom.querySelector("img");
    }
    if (!img) {
      imageRemove.classList.remove("is-visible");
      return;
    }
    var rect = img.getBoundingClientRect();
    var canvasRect = canvas.getBoundingClientRect();
    var left = rect.right - canvasRect.left - 14;
    var top = rect.top - canvasRect.top - 14;
    imageRemove.style.left = Math.max(0, left) + "px";
    imageRemove.style.top = Math.max(0, top) + "px";
    imageRemove.classList.add("is-visible");
  }

  if (editor) {
    editor.on("selectionUpdate", positionRemoveButton);
    editor.on("transaction", positionRemoveButton);
  }

  if (editor && surface) {
    surface.addEventListener("touchstart", function (event) {
      var target = event.target;
      if (!target || target.tagName !== "IMG") return;
      try {
        var pos = editor.view.posAtDOM(target, 0);
        editor.chain().focus().setTextSelection(pos + 1).run();
      } catch (error) {
        editor.chain().focus().run();
      }
    });
  }

  if (imageRemove) {
    imageRemove.addEventListener("click", function () {
      if (!editor) return;
      editor.chain().focus().deleteSelection().run();
      imageRemove.classList.remove("is-visible");
    });
  }

  window.addEventListener("resize", positionRemoveButton);
  window.addEventListener("scroll", positionRemoveButton, true);

  form.addEventListener("submit", function () {
    if (editor) {
      input.value = JSON.stringify(editor.getJSON());
    } else {
      input.value = JSON.stringify(fallbackDoc(surface.innerText.trim()));
    }
  });
})();
