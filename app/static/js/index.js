
// Dropzone.options.dropper = {
//     url: "/upload-pdf",}
{% block scripts %}
Dropzone.autoDiscover = false;
var mydropzone = new Dropzone("#dropper", {
    url: window.origin + "/upload-pdf",
    paramName: "file",
    chunking: true,
    forceChunking: true,
    thumbnailWidth: 120,
    maxFilesize: 60, // megabytes
    maxFiles: 8,
    parallelUploads: 10,
    chunkSize: 1048576,// bytes
    // uploadMultiple:true,
    acceptedFiles: "application/pdf",
    previewContainer: "#dropzone-previws",
    addRemoveLinks: false,
    autoProcessQueue: false,
    // dictRemoveFile: "Remove file",
    addRemoveLinks: true,
    params: function (a, b, c) {
        if (c) {
            return {
                dzuuid: c.file.upload.uuid,
                dzchunkindex: c.index,
                dztotalfilesize: c.file.size,
                dzcurrentchunksize: c.dataBlock.data.size,
                dztotalchunkcount: c.file.upload.totalChunkCount,
                dzchunkbyteoffset: c.index * this.options.chunkSize,
                dzchunksize: this.options.chunkSize,
                dzFilename: c.file.name,
                dir_name: "{{dir_name}}"
            };
        }
    },


    removedfile: function (file) {
        // console.log(file.upload.uuid)
        var name = file.name;
        $.ajax({
            type: 'POST',
            url: window.origin + '/delete',
            data: { "file_name": name, "dir_name": "{{dir_name}}" },
            dataType: 'html'
        });
        var _ref;
        return (_ref = file.previewElement) != null ? _ref.parentNode.removeChild(file.previewElement) : void 0;
    },


})

mydropzone.on("addedfile", function (file) {
    mydropzone.emit("thumbnail", file, "{{url_for('static',filename='images/pdf_icon.gif')}}");
});

document.querySelector(".upload").addEventListener("click", () => {
    mydropzone.processQueue();

})
mydropzone.on("complete", () => {
    mydropzone.files.forEach(
        (file) => {
            if (file.status == 'success' || file.status == 'error') {
                $("#convert").show()
            }
        })
})




$(document).ready(() => {
    $("#convert").on("click", function () {
        console.log("inside convert")
        $.ajax({
            type: 'POST',
            url: window.origin + "/send",
            data: { "dir_name": "{{dir_name}}" },
            dataType: 'json',

            beforeSend: function () {
                $('#loaded').show();
            },
            complete: () => {
                $('#loaded').hide();
            },
            success: (res) => {
                console.log("success")
                console.log(res)
                var form = $(`<form action="/pdfViewer" method="POST" style="display: none;" > 
                        <input type="text" name="output_path" value="${res["output_path"]}" style="display: none;" />
                        </form>`)
                $('body').append(form)
                form.submit()

            },
            error: () => {
                console.log("faild")
            }

        })
    })
})