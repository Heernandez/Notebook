(async function () {
  var nodes = document.querySelectorAll("[data-leaf-id]");
  if (!nodes.length) return;

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

    nodes.forEach(function (node) {
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
      new Editor({
        element: node,
        editable: false,
        extensions: [StarterKit, TextStyle, Color, ImageResize.configure({ inline: true })],
        content: content,
      });
    });
  } catch (error) {
    nodes.forEach(function (node) {
      node.textContent = node.getAttribute("data-leaf-text") || "";
    });
  }
})();
