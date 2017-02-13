#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <kms++/kms++.h>

namespace py = pybind11;

using namespace kms;
using namespace std;

void init_pykmstest(py::module &m);
void init_pykmsbase(py::module &m);
void init_pyvid(py::module &m);

#if HAS_LIBDRM_OMAP
void init_pykmsomap(py::module &m);
#endif

class PyPageFlipHandlerBase : PageFlipHandlerBase
{
public:
	using PageFlipHandlerBase::PageFlipHandlerBase;

	virtual void handle_page_flip(uint32_t frame, double time)
	{
		PYBIND11_OVERLOAD_PURE(
					void,                /* Return type */
					PageFlipHandlerBase, /* Parent class */
					handle_page_flip,    /* Name of function */
					frame, time
					);
	}
};

PYBIND11_PLUGIN(pykms) {
	py::module m("pykms", "kms bindings");

	init_pykmsbase(m);

	py::class_<PageFlipHandlerBase, PyPageFlipHandlerBase>(m, "PageFlipHandlerBase")
			.def(py::init<>())
			.def("handle_page_flip", &PageFlipHandlerBase::handle_page_flip)
			;

	init_pykmstest(m);

	init_pyvid(m);

#if HAS_LIBDRM_OMAP
	init_pykmsomap(m);
#endif
	return m.ptr();
}
