import React, { useState } from "react";
import {
  TextField,
  Button,
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { Container } from "@mui/system";
import axios from "axios";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [tableData, setTableData] = useState([]); 
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setTableData([]);

    try {
      const payload = JSON.stringify({
        user_query: [input],
        model_name: "llama3-70b-8192",
        system_prompt: "Your expert SQL agent",
      });

      const response = await axios.post("http://127.0.0.1:8000/chat", payload, {
        headers: { "Content-Type": "application/json" },
      });

      if (Array.isArray(response.data.results) && response.data.results.length > 0) {
        setTableData(response.data.results); 
      } else {
        const botResponse = { text: response.data.text || "No structured data found", sender: "bot" };
        setMessages((prev) => [...prev, botResponse]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, { text: "Sorry, something went wrong.", sender: "bot" }]);
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ padding: 2, marginTop: 4, borderRadius: 2 }}>
        <Box
          sx={{
            maxHeight: 400,
            overflowY: "auto",
            padding: 2,
            display: "flex",
            flexDirection: "column",
            gap: 1,
          }}
        >
          {messages.map((msg, index) => (
            <Box
              key={index}
              sx={{
                padding: 1,
                borderRadius: 1,
                backgroundColor: msg.sender === "user" ? "#1976d2" : "#f0f0f0",
                color: msg.sender === "user" ? "white" : "black",
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                maxWidth: "80%",
              }}
            >
              <Typography variant="body1">{msg.text}</Typography>
            </Box>
          ))}
        </Box>

        
        {tableData.length > 0 && (
          <TableContainer component={Paper} sx={{ maxHeight: 300, overflowY: "auto", marginTop: 2 }}>
            <Table>
              <TableHead>
                <TableRow>
                  {Object.keys(tableData[0]).map((key) => (
                    <TableCell key={key}>{key}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {tableData.map((row, index) => (
                  <TableRow key={index}>
                    {Object.values(row).map((value, i) => (
                      <TableCell key={i}>{value}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Box sx={{ display: "flex", alignItems: "center", gap: 2, marginTop: 2 }}>
          <TextField
            variant="outlined"
            fullWidth
            placeholder="Message Chatbot..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />
          <Button variant="contained" color="primary" onClick={handleSend}>
            Send
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Chatbot;
