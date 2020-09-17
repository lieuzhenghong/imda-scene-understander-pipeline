#include <gst/gst.h>

/* gst-launch-1.0 -v rtspsrc location="rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream" \
! rtph264depay ! avdec_h264 \
! timeoverlay halignment=right valignment=bottom \
! videorate ! video/x-raw,framerate=60000/1001 ! jpegenc ! multifilesink location="./frame%08d.jpg"
*/

int main(int argc, char *argv[])
{
  GstElement *pipeline;
  GstBus *bus;
  GstMessage *msg;

  /* Initialize GStreamer */
  gst_init(&argc, &argv);

  /* Build the pipeline */

  // pipeline = gst_parse_launch("-v rtspsrc location=rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream ! rtph264depay ! avdec_h264 ! timeoverlay halignment=right valignment=bottom ! videorate ! video/x-raw,framerate=30000/30001 ! jpegenc ! multifilesink location=./frame%08d.jpg", NULL);

  pipeline = gst_parse_launch("-v rtspsrc location=rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream ! rtph264depay ! avdec_h264 ! timeoverlay halignment=right valignment=bottom ! videorate ! video/x-raw,framerate=30000/30001 ! jpegenc ! appsink", NULL);

  // gst_app_sink_pull_sample();

  /* Start playing */
  gst_element_set_state(pipeline, GST_STATE_PLAYING);

  /* Wait until error or EOS */
  bus = gst_element_get_bus(pipeline);
  msg =
      gst_bus_timed_pop_filtered(bus, GST_CLOCK_TIME_NONE,
                                 GST_MESSAGE_ERROR | GST_MESSAGE_EOS);

  /* Free resources */
  if (msg != NULL)
    gst_message_unref(msg);
  gst_object_unref(bus);
  gst_element_set_state(pipeline, GST_STATE_NULL);
  gst_object_unref(pipeline);
  return 0;
}
