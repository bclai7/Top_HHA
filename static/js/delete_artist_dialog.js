$(document).on("click", ".deleteArtistDialog", function () {
 var artist_del_id = this.id;
 var artist_name = artist_del_id.substr(7)
 var message = 'Clicking confirm will delete your rating for <b>' + artist_name + '</b>. Are you sure?'
 $("#confirmationBody").html(message);

 $(".deleteSingleArtist button").val(artist_del_id);
});
