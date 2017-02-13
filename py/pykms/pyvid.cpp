#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <kms++/kms++.h>
#include <kms++util/kms++util.h>
#include <kms++util/videodevice.h>

namespace py = pybind11;

using namespace kms;
using namespace std;

PYBIND11_DECLARE_HOLDER_TYPE(T, T*, true);

// XXX I don't think these are really needed. Use return value parameters.
typedef VideoDevice* VideoDeviceHolder;
typedef VideoStreamer* VideoStreamerHolder;

void init_pyvid(py::module &m)
{
	py::class_<VideoDevice, VideoDeviceHolder>(m, "VideoDevice")
			.def(py::init<const string&>())
			.def_property_readonly("fd", &VideoDevice::fd)
			.def_property_readonly("has_capture", &VideoDevice::has_capture)
			.def_property_readonly("has_output", &VideoDevice::has_output)
			.def_property_readonly("has_m2m", &VideoDevice::has_m2m)
			.def_property_readonly("capture_streamer", &VideoDevice::get_capture_streamer)
			.def_property_readonly("output_streamer", &VideoDevice::get_output_streamer)
			.def_property_readonly("discrete_frame_sizes", &VideoDevice::get_discrete_frame_sizes)
			.def_property_readonly("frame_sizes", &VideoDevice::get_frame_sizes)
			.def("get_capture_devices", &VideoDevice::get_capture_devices)
			;

	py::class_<VideoStreamer, VideoStreamerHolder>(m, "VideoStreamer")
			.def_property_readonly("fd", &VideoStreamer::fd)
			.def_property_readonly("ports", &VideoStreamer::get_ports)
			.def("set_port", &VideoStreamer::set_port)
			.def_property_readonly("formats", &VideoStreamer::get_formats)
			.def("set_format", &VideoStreamer::set_format)
			.def("set_queue_size", &VideoStreamer::set_queue_size)
			.def("queue", &VideoStreamer::queue)
			.def("dequeue", &VideoStreamer::dequeue)
			.def("stream_on", &VideoStreamer::stream_on)
			;
}
