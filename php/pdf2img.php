<?php
# Copyright (c) 2013, Datalogics, Inc. All rights reserved.
#
# This agreement is between Datalogics, Inc. 101 N. Wacker Drive, Suite 1800,
# Chicago, IL 60606 ("Datalogics") and you, an end user who downloads source
# code examples for integrating to the Datalogics (R) PDF Web API (TM)
# ("the Example Code"). By accepting this agreement you agree to be bound
# by the following terms of use for the Example Code.
#
# LICENSE
# -------
# Datalogics hereby grants you a royalty-free, non-exclusive license to
# download and use the Example Code for any lawful purpose. There is no charge
# for use of Example Code.
#
# OWNERSHIP
# ---------
# The Example Code and any related documentation and trademarks are and shall
# remain the sole and exclusive property of Datalogics and are protected by
# the laws of copyright in the U.S. and other countries.
#
# Datalogics and Datalogics PDF Web API are trademarks of Datalogics, Inc.
#
# TERM
# ----
# This license is effective until terminated. You may terminate it at any
# other time by destroying the Example Code.
#
# WARRANTY DISCLAIMER
# -------------------
# THE EXAMPLE CODE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER
# EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
# DATALOGICS DISCLAIM ALL OTHER WARRANTIES, CONDITIONS, UNDERTAKINGS OR
# TERMS OF ANY KIND, EXPRESS OR IMPLIED, WRITTEN OR ORAL, BY OPERATION OF
# LAW, ARISING BY STATUTE, COURSE OF DEALING, USAGE OF TRADE OR OTHERWISE,
# INCLUDING, WARRANTIES OR CONDITIONS OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE, SATISFACTORY QUALITY, LACK OF VIRUSES, TITLE,
# NON-INFRINGEMENT, ACCURACY OR COMPLETENESS OF RESPONSES, RESULTS, AND/OR
# LACK OF WORKMANLIKE EFFORT. THE PROVISIONS OF THIS SECTION SET FORTH
# SUBLICENSEE'S SOLE REMEDY AND DATALOGICS'S SOLE LIABILITY WITH RESPECT
# TO THE WARRANTY SET FORTH HEREIN. NO REPRESENTATION OR OTHER AFFIRMATION
# OF FACT, INCLUDING STATEMENTS REGARDING PERFORMANCE OF THE EXAMPLE CODE,
# WHICH IS NOT CONTAINED IN THIS AGREEMENT, SHALL BE BINDING ON DATALOGICS.
# NEITHER DATALOGICS WARRANT AGAINST ANY BUG, ERROR, OMISSION, DEFECT,
# DEFICIENCY, OR NONCONFORMITY IN ANY EXAMPLE CODE.

error_reporting(E_ALL);
class PDF2IMG {
    /**
     * @var string
     */
    var $base_url;

    /** 
     * @var string
     */
    var $application_id;

    /**
     * @var string
     */
    var $application_key;

    /**
     * @var string
     */
    var $output_format = 'tiff';

    /**
     * @var string
     */
    var $print_preview = TRUE;
  
    /**  
     * @param string     $version Version Number 
     */
    public function __construct($version = 0) {
        $this->parse_arguments($argv);
        $this->base_url = "https://pdfprocess.datalogics-cloud.com/api/"
                           .$version
                           ."/actions/image";
    }  

    /** Set Application ID
     * @param string     $application_id
     */
    public function application_id($application_id) {
        $this->application_id = $application_id;
    }

    /** Set Application Key
     * @param string     $application_key
     */
    public function application_key($application_key) {
        $this->application_key = $application_key; 
    }

    /** Set output file format
     * @param string     $output_format  (jpg, tiff)
     */
    public function output_format($output_format = "jpg") {
        $this->output_format = $output_format;
    } 
 
    /** Set print preview
     * @param bool     $print_preview (true, false)
     */
    public function print_preview($print_preview = TRUE) {
       $this->print_preview = $print_preview;
    }
  

    /** Call server to convert file
     * @param string     $source_file_name Input file name
     * @param string     $destination_file_name Output file name
     */
    public function convert($source_file_name, $destination_file_name) {
        $ch = curl_init($this->base_url);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $this->prepare_request($source_file_name));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);  
        curl_setopt($ch, CURLOPT_VERBOSE, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: multipart/form-data'));
        $response = curl_exec($ch);
        curl_close($ch);
        $this->handle_response($response, $destination_file_name);
    }
    /** Handle server response
     * @param JSONObject     $response Server Response 
     * @param string         $destination_file_name output file name
     */
    public function handle_response($response, $destination_file_name) {
        $json_decoded = json_decode($response);
        $output = base64_decode($json_decoded->output);
        $process_code = base64_decode($json_decoded->processCode);
    
        if ($process_code != 0)
        {
            printf('ERROR: '.$process_code."\n")
            printf('Error Message: '.$output."\n")
            exit($process_code)
        }
    
        $file = fopen($destination_file_name, "wb");
        fwrite($file, $output);
        fclose($file);
    }
    private function parse_arguments($arguments) {
    
    }
    private function prepare_request($file_name) {
        $fields = array(
          'application' => $this->prepare_application_json(), 
          'inputName' => basename($file_name),
          'options' => $this->prepare_options_json(),
          'input' => "@$file_name"
        );
        return $fields;
    }

    private function prepare_options_json() {
        $options = array();
        $options['outputForm'] = $this->output_format;
        if ($this->print_preview) {
            $options['printPreview'] = TRUE;
        }
        return json_encode($options);
    }
  
    private function prepare_application_json() {
        $application = array('id' => $this->application_id,
                             'key' => $this->application_key);
        return json_encode($application);
    }
}

// Driver code
$source_file_name = "./test.pdf";
$destination_file_name = "converted.jpg";
$pdf2img = new PDF2IMG();
$pdf2img->application_id = 'TODO: Application ID'; 
$pdf2img->application_key = 'TODO: Applicaiton Key';
$pdf2img->output_format = 'tiff';
$pdf2img->print_preview = FALSE;
$pdf2img->convert($source_file_name, $destination_file_name);

?>
