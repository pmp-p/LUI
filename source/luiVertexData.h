// Filename: luiVertexData.h
// Created by:  tobspr (01Sep14)
//

#ifndef LUI_VERTEX_DATA_H
#define LUI_VERTEX_DATA_H

#include "pandabase.h"
#include "pandasymbols.h"
#include "luse.h"

#include <stdint.h>

struct LUIVertexData {
  PN_stdfloat x, y, z;
  unsigned char color[4];
  PN_stdfloat u, v;
  uint16_t texindex;
};

#endif
