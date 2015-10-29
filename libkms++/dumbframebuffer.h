#pragma once

#include "framebuffer.h"
#include "pixelformats.h"

namespace kms
{
class DumbFramebuffer : public Framebuffer
{
public:
	DumbFramebuffer(Card& card, uint32_t width, uint32_t height, const std::string& fourcc);
	DumbFramebuffer(Card& card, uint32_t width, uint32_t height, PixelFormat format);
	virtual ~DumbFramebuffer();

	void print_short() const;

	PixelFormat format() const { return m_format; }
	unsigned num_planes() const { return m_num_planes; }

	uint32_t handle(unsigned plane) const { return m_planes[plane].handle; }
	uint8_t* map(unsigned plane) const { return m_planes[plane].map; }
	uint32_t stride(unsigned plane) const { return m_planes[plane].stride; }
	uint32_t size(unsigned plane) const { return m_planes[plane].size; }
	uint32_t offset(unsigned plane) const { return m_planes[plane].offset; }
	uint32_t prime_fd(unsigned plane);

	void clear();

private:
	struct FramebufferPlane {
		uint32_t handle;
		int prime_fd;
		uint32_t size;
		uint32_t stride;
		uint32_t offset;
		uint8_t *map;
	};

	void Create();
	void Destroy();

	unsigned m_num_planes;
	struct FramebufferPlane m_planes[4];

	PixelFormat m_format;
};
}
