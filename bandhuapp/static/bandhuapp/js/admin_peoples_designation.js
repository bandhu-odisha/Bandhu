(function () {
  function roleSelectsForDesignation(designationSelect) {
    const name = designationSelect.getAttribute("name") || "";
    if (name === "designation") {
      return [document.getElementById("id_role")].filter(Boolean);
    }
    const prefix = name.replace(/-designation$/, "");
    return Array.from(
      document.querySelectorAll('select[name="' + prefix + '-role"]')
    );
  }

  function filterRoleOptions(designationSelect) {
    const designationId = designationSelect.value;
    roleSelectsForDesignation(designationSelect).forEach(function (roleSelect) {
      let visibleCount = 0;
      Array.from(roleSelect.options).forEach(function (option) {
        if (!option.value) {
          option.hidden = false;
          return;
        }
        const roleDesignationId = option.getAttribute("data-designation-id");
        const hasDesignationTag = roleDesignationId !== null && roleDesignationId !== "";
        const show =
          !designationId ||
          !hasDesignationTag ||
          roleDesignationId === designationId;
        option.hidden = !show;
        if (show) {
          visibleCount += 1;
        }
        if (!show && option.selected) {
          option.selected = false;
          roleSelect.value = "";
        }
      });
      // If filtering hid everything (e.g. missing data attrs), show all role options.
      if (designationId && visibleCount === 0) {
        Array.from(roleSelect.options).forEach(function (option) {
          option.hidden = false;
        });
      }
    });
  }

  function bindDesignationSelect(designationSelect) {
    if (designationSelect.dataset.peoplesDesignationBound) {
      return;
    }
    designationSelect.dataset.peoplesDesignationBound = "1";
    designationSelect.addEventListener("change", function () {
      filterRoleOptions(designationSelect);
    });
    filterRoleOptions(designationSelect);
  }

  function init() {
    document
      .querySelectorAll('select[name$="-designation"], select#id_designation')
      .forEach(bindDesignationSelect);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  document.addEventListener("formset:added", function (event) {
    const row = event.target;
    if (!row || !row.querySelector) {
      return;
    }
    row
      .querySelectorAll('select[name$="-designation"]')
      .forEach(bindDesignationSelect);
  });
})();
