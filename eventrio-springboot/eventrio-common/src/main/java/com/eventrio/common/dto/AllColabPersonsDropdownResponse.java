package com.eventrio.common.dto;

import lombok.Data;

@Data
public class AllColabPersonsDropdownResponse {

    private String docID;

    private String userAccID;

    private String personName;

    private String status;

    private String email;
}
