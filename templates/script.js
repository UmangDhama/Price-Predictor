$(document).ready(function() {
  // get the checkbox inputs and input fields
  var featureCheckboxes = $("input[name='features']");
  var inputFields = $(".input-field");

  // hide all input fields initially
  inputFields.hide();

  // add event listener to the checkbox inputs
  featureCheckboxes.change(function() {
      var feature = $(this).val();
      var inputField = $("#" + feature + "-input-field");
      if ($(this).is(":checked")) {
          inputField.show();
      } else {
          inputField.hide();
      }
  });

  // add event listener to the form submission
  $("form").submit(function(e) {
      // prevent the default form submission
      e.preventDefault();

      // collect the selected features and their values
      var formData = {};
      featureCheckboxes.each(function() {
          var feature = $(this).val();
          var inputField = $("#" + feature + "-input-field");
          if ($(this).is(":checked")) {
              formData[feature] = inputField.find("input").val();
          }
      });

      // send an AJAX POST request to the server
      $.ajax({
          type: "POST",
          url: "/predict_select",
          data: JSON.stringify(formData),
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          success: function(response) {
              // handle the response from the server
              console.log(response); // log the response for testing
          },
          error: function(xhr, status, error) {
              // handle any errors that occurred during the request
              console.log("Error: " + error); // log the error for testing
          }
      });
  });
});
