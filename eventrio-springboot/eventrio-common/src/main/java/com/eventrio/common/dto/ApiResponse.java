package com.eventrio.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

    private String message;
    private T data;
    private String error;

    public static <T> ApiResponse<T> success(String message, T data) {
        return ApiResponse.<T>builder().message(message).data(data).build();
    }

    public static ApiResponse<String> fail(String message, String detail) {
        return ApiResponse.<String>builder().message(message).data(detail).build();
    }

    public static <T> ApiResponse<T> error(String message, T data) {
        return ApiResponse.<T>builder().message(message).data(data).build();
    }

    public static ApiResponse<String> errorMessage(String message, String data) {
        return fail(message, data);
    }
}
