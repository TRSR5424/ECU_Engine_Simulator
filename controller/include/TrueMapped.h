/** @file TrueMapped.h
 *  @brief Native controller TrueMapped implementation.
 */

#ifndef TRUE_MAPPED_H
#define TRUE_MAPPED_H

#include "Controller.h"

class TrueMapped : public Controller {
public:
    TrueMapped();
    double compute(const ControllerInput& input) override;
};

#endif // TRUE_MAPPED_H