
function loadData() {

    var $body = $('body');
    var $wikiElem = $('#wikipedia-links');
    var $nytHeaderElem = $('#nytimes-header');
    var $nytElem = $('#nytimes-articles');
    var $greeting = $('#greeting');

    // clear out old data before new request
    $wikiElem.text("");
    $nytElem.text("");

    // load streetview
    var $street = $("#street").val();
    var $city = $("#city").val();
    var $imgSrc = "https://maps.googleapis.com/maps/api/streetview?size=600x300&location=" + $street + "," + $city + "&key=AIzaSyC2EdNiUT1XhEN0qpvDP4tKvV3BzKke-34"
    var $imgElem = '<img class="bgimg" src="' + $imgSrc + '">'

    //append image to DOM
    $body.append($imgElem);


    //NYT API
    var url = "https://api.nytimes.com/svc/search/v2/articlesearch.json";
    url += '?' + $.param({
      'api-key': "23da1dc6004c4c34ae251a5aa9082df3",
      'q': $city
    });

    //Get articles and add them to the unordered list
    $.getJSON( url, function( data ) {
      var items = [];
      $.each( data.response.docs, function( key, val ) {
        items.push( "<li class='article'><a href='"+ val.web_url + "' target='_blank'>" + val.headline.main + "</a><p>" + val.snippet + "</p></li>" );
      });
        console.log(data);
     
      $( "<ul/>", {
        "class": "nytimes-articles",
        html: items.join( "" )
      }).appendTo( "body" );
    }).error(function(e) {
        $nytHeaderElem.text('New York Times Articles could not be loaded.');
    });

    return false;
};

$('#form-container').submit(loadData);
