window.onload = function loadCriteria(){
  // Store session variable
  var session = {{ session | tojson }}; // session variable
  var categoryList = {{ categoryList | tojson }}; // list of categories

  // For each rating, set the the corresponding slider value
  for(i=0; i < categoryList.length; i++){
    var slider_name = "criteria_"+categoryList[i];
    document.getElementById(slider_name).value = session[categoryList[i]];
  }

  // Show slider scores in HTML
  for(i=0; i<categoryList.length;  i++){
    // First get reference to slider to get its vlaue
    var active_slider_name = "criteria_"+categoryList[i];
    var activeSliderValue = document.getElementById(active_slider_name).value;

    // Then update the score element for the corresponding category
    var scoreElementName = 'criteria_score_'+categoryList[i];
    document.getElementById(scoreElementName).innerHTML = activeSliderValue;
  }
}

function showSliderValues(){
  var categoryList = {{ categoryList | tojson }}; // list of categories
  for(i=0; i<categoryList.length;  i++){
    // First get reference to slider to get its vlaue
    var active_slider_name = "criteria_"+categoryList[i];
    var activeSliderValue = document.getElementById(active_slider_name).value;

    // Then update the score element for the corresponding category
    var scoreElementName = 'criteria_score_'+categoryList[i];
    document.getElementById(scoreElementName).innerHTML = activeSliderValue;
  }
}

function resetSliders(){
  setTimeout(function(){
      showSliderValues();
  }, 0);
  return true;
}

// Function to ensure that the combined max values of the sliders equal 100
function maxCombinedValues(activeCategory){
  var categoryList = {{ categoryList | tojson }}; // list of categories
  var totalValue=0; // total value between all sliders
  var active_slider_name = "criteria_"+activeCategory;

  for(i=0; i < categoryList.length; i++){
    var slider_name = "criteria_"+categoryList[i];
    totalValue += Number(document.getElementById(slider_name).value);
  }
  if(totalValue > 100){
    // get combined values of other sliders
    var other_sliders_value = 0;
    for(i=0; i < categoryList.length; i++){
      var slider_name = "criteria_"+categoryList[i];
      if(slider_name != active_slider_name){
        other_sliders_value += Number(document.getElementById(slider_name).value);
      }
    }
    var newVal = 100 - other_sliders_value;
    document.getElementById(active_slider_name).value = newVal;

  }
}
