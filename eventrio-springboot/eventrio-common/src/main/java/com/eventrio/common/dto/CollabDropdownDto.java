package com.eventrio.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CollabDropdownDto {
    private String docID;
    private String userAccID;
    private String personName;
    private String status;
    private String email;
}
