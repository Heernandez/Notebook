(async function () {
  var nodes = document.querySelectorAll("[data-leaf-id]");
  if (!nodes.length) return;
  var stage = document.querySelector("[data-reader]");
  var pages = stage ? stage.querySelectorAll(".reader-page") : null;

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

  function getContent(node) {
    var page = node.closest(".reader-page");
    var script = page ? page.querySelector('script[type="application/json"]') : null;
    var raw = script ? script.textContent : "";
    var content = null;
    if (raw) {
      try {
        content = JSON.parse(raw);
        if (typeof content === "string") {
          content = JSON.parse(content);
        }
      } catch (error) {
        content = null;
      }
    }
    if (!content || !content.type || !content.content) {
      var textFallback = node.getAttribute("data-leaf-text") || "";
      content = fallbackDoc(textFallback);
    }
    return content;
  }

  nodes.forEach(function (node) {
    if (!node.textContent) {
      node.textContent = node.getAttribute("data-leaf-text") || "";
    }
  });

  try {
    var modules = await Promise.all([
      import("https://esm.sh/@tiptap/core@2.6.6"),
      import("https://esm.sh/@tiptap/starter-kit@2.6.6"),
      import("https://esm.sh/tiptap-extension-resize-image@1.3.2"),
      import("https://esm.sh/@tiptap/extension-text-style@2.6.6"),
      import("https://esm.sh/@tiptap/extension-color@2.6.6"),
    ]);
    var Editor = modules[0].Editor;
    var StarterKit = modules[1].StarterKit || modules[1].default;
    var ImageResize = modules[2].default || modules[2];
    var TextStyle = modules[3].TextStyle || modules[3].default;
    var Color = modules[4].Color || modules[4].default;

    function mountEditor(node) {
      if (!node || node.dataset.editorReady === "true") return;
      node.dataset.editorReady = "true";
      var content = getContent(node);
      new Editor({
        element: node,
        editable: false,
        extensions: [StarterKit, TextStyle, Color, ImageResize.configure({ inline: true })],
        content: content,
      });
    }

    function mountAdjacent(index) {
      if (!pages || !pages.length) {
        mountEditor(nodes[index]);
        return;
      }
      var targets = [index - 1, index, index + 1];
      targets.forEach(function (targetIndex) {
        if (targetIndex < 0 || targetIndex >= pages.length) return;
        var node = pages[targetIndex].querySelector("[data-leaf-id]");
        mountEditor(node);
      });
    }

    if (stage && pages && pages.length) {
      stage.addEventListener("reader:page", function (event) {
        if (!event || !event.detail) return;
        var index = Number(event.detail.index || 0);
        mountAdjacent(index);
      });
      mountAdjacent(0);
    } else if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              mountEditor(entry.target);
            }
          });
        },
        {
          root: stage || null,
          rootMargin: "50% 0px",
          threshold: 0.01,
        }
      );
      nodes.forEach(function (node, index) {
        observer.observe(node);
        if (index === 0) mountEditor(node);
      });
    } else {
      nodes.forEach(function (node) {
        mountEditor(node);
      });
    }
  } catch (error) {
    nodes.forEach(function (node) {
      node.textContent = node.getAttribute("data-leaf-text") || "";
    });
  }
})();
