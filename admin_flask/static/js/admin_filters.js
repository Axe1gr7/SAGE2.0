// Shared helpers for admin filters (currently lightweight)
(function(){
  function debounce(fn, ms){
    let t; return function(){
      clearTimeout(t);
      const args = arguments;
      t = setTimeout(()=>fn.apply(null,args), ms);
    };
  }

  // Example: auto-submit on select change (optional)
  function autoSubmitOnChange(selectEl, formEl){
    const onChange = debounce(()=>{
      if(selectEl && formEl) formEl.submit();
    }, 150);
    if(selectEl) selectEl.addEventListener('change', onChange);
  }

  window.adminFilters = { debounce, autoSubmitOnChange };
})();

