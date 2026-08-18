const installedRoots = new WeakSet();
const activePointerState = new WeakMap();

function findElement(target, selector, root) {
  if (!target || !target.closest) {
    return null;
  }

  const element = target.closest(selector);
  if (!element || !root.contains(element)) {
    return null;
  }

  return element;
}

function isInteractiveControl(target) {
  return Boolean(target?.closest?.("button, input, select, textarea, a, summary, details, [data-dnd-no-drag='true']"));
}

function scrollPageNearViewportEdge(clientY) {
  const edgeSize = 72;
  const maxStep = 56;
  let scrollStep = 0;

  if (clientY < edgeSize) {
    scrollStep = -Math.ceil(((edgeSize - clientY) / edgeSize) * maxStep);
  } else if (clientY > window.innerHeight - edgeSize) {
    scrollStep = Math.ceil(((clientY - (window.innerHeight - edgeSize)) / edgeSize) * maxStep);
  }

  if (scrollStep !== 0) {
    window.scrollBy({ top: scrollStep, behavior: "auto" });
  }
}

export function attachDragPayloads(root, dotnetRef) {
  if (!root || installedRoots.has(root)) {
    return;
  }

  installedRoots.add(root);

  const getDropZone = (x, y) => findElement(document.elementFromPoint(x, y), "[data-dnd-dropzone='true']", root);

  const clearHover = () => {
    root.querySelectorAll(".drag-hover").forEach((element) => {
      element.classList.remove("drag-hover");
    });
  };

  root.addEventListener("pointerdown", (event) => {
    if (isInteractiveControl(event.target)) {
      return;
    }

    const dragSource = findElement(event.target, "[data-dnd-payload]", root);
    if (!dragSource) {
      return;
    }

    activePointerState.set(root, {
      payload: dragSource.dataset.dndPayload || "",
      source: dragSource,
      pointerId: event.pointerId
    });

    if (dragSource.setPointerCapture) {
      dragSource.setPointerCapture(event.pointerId);
    }

    event.preventDefault();
  });

  root.addEventListener("dragstart", (event) => {
    const dragSource = findElement(event.target, "[data-dnd-payload]", root);
    if (!dragSource) {
      return;
    }

    event.dataTransfer?.setData("text/plain", dragSource.dataset.dndPayload || "");
    event.dataTransfer?.setDragImage(dragSource, 20, 20);
  });

  root.addEventListener("dragover", (event) => {
    const state = activePointerState.get(root);
    const payload = state?.payload || event.dataTransfer?.getData("text/plain");
    if (!payload) {
      return;
    }

    event.preventDefault();
    const dropZone = getDropZone(event.clientX, event.clientY);
    clearHover();
    if (dropZone) {
      dropZone.classList.add("drag-hover");
    }
  });

  root.addEventListener("drop", async (event) => {
    const payload = activePointerState.get(root)?.payload || event.dataTransfer?.getData("text/plain");
    if (!payload) {
      return;
    }

    event.preventDefault();
    const dropZone = getDropZone(event.clientX, event.clientY);
    clearHover();
    if (dropZone) {
      const dayIndex = Number.parseInt(dropZone.dataset.dayIndex || "", 10);
      const mealSlot = dropZone.dataset.mealSlot || "";
      if (!Number.isNaN(dayIndex) && mealSlot) {
        await dotnetRef.invokeMethodAsync("HandleExternalDrop", payload, dayIndex, mealSlot);
      }
    }

    activePointerState.delete(root);
  });

  root.addEventListener("pointermove", (event) => {
    const state = activePointerState.get(root);
    if (!state?.payload) {
      return;
    }

    scrollPageNearViewportEdge(event.clientY);
    const dropZone = getDropZone(event.clientX, event.clientY);
    clearHover();
    if (dropZone) {
      dropZone.classList.add("drag-hover");
    }
  });

  root.addEventListener("pointerup", async (event) => {
    const state = activePointerState.get(root);
    if (!state?.payload) {
      return;
    }

    const dropZone = getDropZone(event.clientX, event.clientY);
    clearHover();

    if (dropZone) {
      const dayIndex = Number.parseInt(dropZone.dataset.dayIndex || "", 10);
      const mealSlot = dropZone.dataset.mealSlot || "";
      if (!Number.isNaN(dayIndex) && mealSlot) {
        await dotnetRef.invokeMethodAsync("HandleExternalDrop", state.payload, dayIndex, mealSlot);
      }
    }

    activePointerState.delete(root);
  });

  root.addEventListener("pointercancel", () => {
    clearHover();
    activePointerState.delete(root);
  });
}
